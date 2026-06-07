from collections import deque
from backtester.data import DataHandler
from backtester.strategy import Strategy
from backtester.portfolio import Portfolio
from backtester.execution import Executor

class Simulation:
    def __init__(self, tickers:list):
        self.queue = deque()
        self.bars = DataHandler(tickers)
        self.strategy = Strategy(self.bars)
        self.portfolio = Portfolio(10000)
        self.executor = Executor(self.bars)
    
    def simulate(self):
        while True:
            ret_event = None
            self.bars.updateBar();
            ret_event = self.queue.popleft() 
            if event.type == "KILL":
                print("Terminating")
                break
            elif event.type == "MARKET":
                ret_event = self.strategy.on_market();
            elif event.type == "SIGNAL":
                ret_event = self.portfolio.handle_signal(event);
            elif event.type == "ORDER":
                ret_event = self.executor.handle_order(event);
            elif event.type == "FILL":
                _ = self.portfolio.handle_fill_event(event)
            else:
                raise NotImplementedError
            
            if ret_event:
                for event in ret_event:
                    self.queue.append(event)

    def metrics(self):
        return 0
    
if __name__ == "__main__":
    sim = Simulation(["aapl", "msft"])
    sim.simulate()
