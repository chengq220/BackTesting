from collections import deque
from backtester.data import DataHandler
from backtester.strategy import Strategy
from backtester.portfolio import Portfolio

class Simulation:
    def __init__(self, tickers:list):
        self.queue = deque()
        self.bars = DataHandler(tickers, self.queue)
        self.strategy = Strategy(self.bars, self.queue)
        self.portfolio = Portfolio()
        # broker = execution
    
    def simulate(self):
        while True:
            self.bars.updateBar();
            event = self.queue.popleft() 
            if event.type == "KILL":
                print("Terminating")
                break
            elif event.type == "MARKET":
                self.strategy.on_market();
            elif event.type == "SIGNAL":
                self.portfolio.handle_signal(event);
            # elif event.type == "ORDER":
            #     self.broker.handle_order(event);
            # elif event.type == "FILL":
            #     self.portfolio.handle_fill(event)

    def metrics(self):
        return 0
    
if __name__ == "__main__":
    sim = Simulation(["aapl", "msft"])
    sim.simulate()
