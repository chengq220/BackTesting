from collections import deque
from backtester.data import DataHandler
from backtester.strategy import Strategy
from backtester.portfolio import Portfolio
from backtester.execution import Executor

class Simulation:
    def __init__(self, tickers:list):
        self.__queue = deque()
        self.__bars = DataHandler(tickers)
        self.__strategy = Strategy(self.__bars)
        self.__portfolio = Portfolio(10000)
        self.__executor = Executor("NASDAQ", self.__bars)
    
    def update_queue(self, events):
        for event in events:
            self.__queue.append(event)

    def simulate(self):
        while True:
            self.update_queue(self.__bars.updateBar())
            event = self.__queue.popleft() 

            if event.type == "KILL":
                print("Terminating")
                break
            elif event.type == "MARKET":
                prices = {}
                for tick in self.__bars.tickers:
                    prices[tick.upper()] = self.__bars.get_last_N_bars(tick, 1)[-1].item()
                _ = self.__portfolio.on_market(prices)
                self.update_queue(self.__strategy.on_market())
            elif event.type == "SIGNAL":
                self.update_queue(self.__portfolio.handle_signal_event(event))
            elif event.type == "ORDER":
                self.update_queue(self.__executor.execute_order(event))
            elif event.type == "FILL":
                _ = self.__portfolio.handle_fill_event(event)
            else:
                raise NotImplementedError
    
    def get_portfolio_history(self):
        return self.__portfolio.portfolio_history
    
    def metrics(self):
        return 0
    
if __name__ == "__main__":
    sim = Simulation(["msft"])
    sim.simulate()
    print(sim.get_portfolio_history())
