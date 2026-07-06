from collections import deque
from backtester.data import DataHandler
from backtester.strategy import StrategyContainer as Strategy
from backtester.portfolio import Portfolio
from backtester.execution import Executor
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np

class Simulation:
    def __init__(self, tickers:list, strategy:str, start:str, end:str, inital_captial:int):
        self.__queue = deque()
        self.__bars = DataHandler(tickers, start, end)
        self.__strategy = Strategy(self.__bars, strat=strategy)
        self.__portfolio = Portfolio(inital_captial, sizing_rule = 2000)
        self.__executor = Executor("NASDAQ", self.__bars)
        self.__portfolio_init = False
    
    def __update_queue(self, events):
        for event in events:
            self.__queue.append(event)

    def __compute_prices(self):
        prices = {}
        for tick in self.__bars.tickers:
            prices[tick] = self.__bars.get_last_N_bars(tick, 1)[-1].item()
        return prices

    def run_one_epoch(self, manual_terminate = False):
        # initialize the portfolio 
        if not self.__portfolio_init:
            _ = self.__portfolio.init_portfolio(self.__bars.tickers)
            self.__portfolio_init = True

        terminate = False
        self.__update_queue(self.__bars.updateBar())
        while len(self.__queue) > 0:
            event = self.__queue.popleft()
            if event.type == "KILL":
                print("Terminating")
                # At termination, return the portfolio to OUT position for all stocks
                self.__update_queue(self.__portfolio.exit_position())
                terminate = True
            elif event.type == "MARKET":
                cur_day = self.__bars.get_current_day()
                prices = self.__compute_prices()
                _ = self.__portfolio.on_market(prices)
                res = self.__strategy.on_market(cur_day)
                self.__update_queue(res)
            elif event.type == "SIGNAL":
                cur_day = self.__bars.get_current_day()
                res = self.__portfolio.handle_signal_event(event, cur_day)
                self.__update_queue(res)
            elif event.type == "ORDER":
                cur_day = self.__bars.get_current_day()
                res = self.__executor.execute_order(event, cur_day)
                self.__update_queue(res)
            elif event.type == "FILL":
                cur_day = self.__bars.get_current_day()
                res = self.__portfolio.handle_fill_event(event, cur_day)
                if res:
                    self.__update_queue(res)
            else:
                print("You are not suppose to be here!")
                raise NotImplementedError
        
        if manual_terminate:
            prices = self.__compute_prices()
            self.__portfolio.on_market(prices)

        return terminate

    def run_all(self, backtest = True):
        # Double while loops make sure that each bar are separated events so no mixing events between days
        # This avoids having multiple market events in the queue
        terminate = False
        while backtest and not terminate:
            terminate_signal = self.run_one_epoch()
            terminate = terminate or terminate_signal 

        # Update the portfolio history after exiting all positions 
        prices = self.__compute_prices()
        self.__portfolio.on_market(prices)


    def get_portfolio_history(self):
        processed = defaultdict(list)
        end_cash, portfolio_history = self.__portfolio.get_portfolio_stats()
        print(f"Ending cash: ${end_cash}")
        for idx in range(len(portfolio_history)):
            cur_dict = portfolio_history[idx]
            for key in cur_dict.keys():
                processed[key].append(cur_dict[key])
        return processed
    
if __name__ == "__main__":
    sim = Simulation(["IVV"], start="2009-12-01", end="2010-6-01", inital_captial=10000, strategy="DCA")
    sim.run_one_epoch(manual_terminate=True)
    # sim.run_all()
    hist = sim.get_portfolio_history()

    t = np.arange(0, len(hist["equity"]))
    plt.plot(t, hist["equity"], linestyle = 'dotted')
    plt.plot(t, hist["free_cash"], linestyle = 'solid')
    plt.show()
