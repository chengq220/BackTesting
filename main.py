from collections import deque
from backtester.data import DataHandler
from backtester.strategy import Strategy
from backtester.event import MarketEvent

class Simulation:
    def __init__(self, tickers:list):
        self.queue = deque()
        self.bars = DataHandler(tickers, self.queue)
        self.strategy = Strategy(self.bars, self.queue)
        # portfolio = portfolio
        # broker = execution
    
    def simulate(self):
        event = self.bars.updateBar();
        while self.queue():
            if event.type == "KILL":
                break
            elif event.type == "MARKET":
                self.strategy.calculate_trading_signals(event);
            elif event.type == "SIGNAL":
                self.portfolio.handle_signal(event);
            elif event.type == "ORDER":
                self.portfolio.handle_order(event);
            elif event.type == "FILL":
                self.portfolio.handle_fill(event)

    def metrics(self):
        return 0
    
if __name__ == "__main__":
    sim = Simulation(["aapl", "msft"])
