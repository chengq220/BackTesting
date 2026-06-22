from collections import deque
from backtester.data import DataHandler
from backtester.strategyContainer import StrategyContainer as Strategy
from backtester.portfolio import Portfolio
from backtester.execution import Executor
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np

class Simulation:
    def __init__(self, tickers:list):
        self.__queue = deque()
        self.__bars = DataHandler(tickers)
        self.__strategy = Strategy(self.__bars, inst="DCA")
        self.__portfolio = Portfolio(10000, sizing_rule = "10000")
        self.__executor = Executor("NASDAQ", self.__bars)
    
    def __update_queue(self, events):
        for event in events:
            self.__queue.append(event)

    def simulate(self, backtest = True):
        terminate = False
        # Double while loops make sure that each bar are separated events so no mixing events between days
        # This avoids having multiple market events in the queue
        while backtest and not terminate:
            self.__update_queue(self.__bars.updateBar())
            while len(self.__queue) > 0:
                event = self.__queue.popleft()
                if event.type == "KILL":
                    print("Terminating")
                    terminate = True
                elif event.type == "MARKET":
                    prices = {}
                    for tick in self.__bars.tickers:
                        prices[tick] = self.__bars.get_last_N_bars(tick, 1)[-1].item()
                    _ = self.__portfolio.on_market(prices)
                    res = self.__strategy.on_market()
                    self.__update_queue(res)
                elif event.type == "SIGNAL":
                    res = self.__portfolio.handle_signal_event(event)
                    self.__update_queue(res)
                elif event.type == "ORDER":
                    res = self.__executor.execute_order(event)
                    self.__update_queue(res)
                elif event.type == "FILL":
                    res = self.__portfolio.handle_fill_event(event)
                    if res:
                        self.__update_queue(res)
                else:
                    print(event)
                    print("You are not suppose to be here!")
                    raise NotImplementedError
    
    def get_portfolio_history(self):
        processed = defaultdict(list)
        for idx in range(len(self.__portfolio.portfolio_history)):
            cur_dict = self.__portfolio.portfolio_history[idx]
            for key in cur_dict.keys():
                processed[key].append(cur_dict[key])
        return processed
    
if __name__ == "__main__":
    sim = Simulation(["IVV"])
    sim.simulate()
    hist = sim.get_portfolio_history()

    t = np.arange(0, len(hist["equity"]))
    plt.plot(t, hist["equity"], linestyle = 'dotted')
    plt.plot(t, hist["free_cash"], linestyle = 'solid')
    plt.show()
