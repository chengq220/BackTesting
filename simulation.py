from collections import deque
from backtester.data import DataHandler
from backtester.strategy import StrategyContainer as Strategy
from backtester.portfolio import Portfolio
from backtester.execution import Executor
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np

class Simulation:
    def __init__(self, tickers:list, strategy:dict, start:str, end:str, inital_captial:int):
        self.__queue = deque()
        self.__bars = DataHandler(tickers, start, end)
        self.__strategy = Strategy(self.__bars, strat_dict=strategy)
        self.__portfolio = Portfolio(inital_captial, sizing_rule = 2000)
        self.__executor = Executor("NASDAQ", self.__bars)

    # initialize the portfolio 
    def initialize_portfolio(self):
        _ = self.__portfolio.init_portfolio(self.__bars.tickers)
        self.portfolio_init = True

    def __update_queue(self, events):
        for event in events:
            self.__queue.append(event)

    def __compute_prices(self):
        prices = {}
        for tick in self.__bars.tickers:
            prices[tick] = self.__bars.get_last_N_bars(tick, 1)[-1].item()
        return prices

    def run_one_epoch(self, manual_terminate = True):
        terminate = False
        self.__update_queue(self.__bars.updateBar())
        while len(self.__queue) > 0:
            event = self.__queue.popleft()
            cur_day = self.__bars.get_current_day()
            if event.type == "KILL":
                print("Terminating")
                # At termination, return the portfolio to OUT position for all stocks
                self.__update_queue(self.__portfolio.exit_position(cur_day))
                terminate = True
            elif event.type == "MARKET":
                prices = self.__compute_prices()
                _ = self.__portfolio.on_market(prices, date = cur_day)
                res = self.__strategy.on_market(cur_day)
                self.__update_queue(res)
            elif event.type == "SIGNAL":
                res = self.__portfolio.handle_signal_event(event, cur_day)
                self.__update_queue(res)
            elif event.type == "ORDER":
                res = self.__executor.execute_order(event, cur_day)
                self.__update_queue(res)
            elif event.type == "FILL":
                res = self.__portfolio.handle_fill_event(event, cur_day)
                if res:
                    self.__update_queue(res)
            else:
                print("You are not suppose to be here!")
                raise NotImplementedError
        
        if manual_terminate:
            prices = self.__compute_prices()
            terminate_date = self.__bars.get_current_day()
            self.__portfolio.on_market(prices, terminate_date)

        return terminate

    def run_all(self, backtest = True):
        # Double while loops make sure that each bar are separated events so no mixing events between days
        # This avoids having multiple market events in the queue
        terminate = False
        while backtest and not terminate:
            terminate_signal = self.run_one_epoch(manual_terminate=False)
            terminate = terminate or terminate_signal 

        # Update the portfolio history after exiting all positions 
        prices = self.__compute_prices()
        terminate_date = self.__bars.get_current_day()
        self.__portfolio.on_market(prices, terminate_date)


    def get_portfolio_history(self):
        processed = defaultdict(list)
        end_cash, portfolio_history = self.__portfolio.get_portfolio_stats()
        print(portfolio_history)
        print(f"Ending cash: ${end_cash}")
        for idx in range(len(portfolio_history)):
            cur_dict = portfolio_history[idx]
            for key in cur_dict.keys():
                processed[key].append(cur_dict[key])
        return processed
    
if __name__ == "__main__":
    strategy = {
        "strategy": "DCA",
        "strategy_param": None
    }
    sim = Simulation(["IVV"], start="2023-12-01", end="2024-6-01", inital_captial=10000, strategy=strategy)
    # sim.run_one_epoch(manual_terminate=Fa)
    sim.run_all()
    hist = sim.get_portfolio_history()

    # t = np.arange(0, len(hist["equity"]))
    # plt.plot(t, hist["equity"], linestyle = 'dotted')
    # plt.plot(t, hist["free_cash"], linestyle = 'solid')
    # plt.show()
