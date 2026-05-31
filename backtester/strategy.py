from backtester.event import SignalEvent
from time import time


# Answer the question "what is my directional view right now?"
class Strategy:
    def __init__(self, data_handler, queue):
        # The market data
        self.data = data_handler

        # The action queue 
        self.q = queue

        self.tickers = self.data.tickers

        # initialize the direction to "OUT" because there is no 
        # position (other choices are SHORT/LONG)
        self.direction = {}
        for symb in self.tickers:
            self.direction[symb.upper()] = "OUT"
            
    # On market event, pulls the latest bars, and generate signal and add those signals back to the queue
    def on_market(self):
        # Generate Signal Events for each of the tickers
        for symb in self.tickers:
            symb_direction = self.generate_signal(symb)
            self.q.append(symb_direction)

    # Strategy used to generate the signals
    def generate_signal(self, ticker, N = 10):
        direction = "short" #TODO need to add the logic for the signals
        datetime = time.time()
        output = SignalEvent(ticker, datetime, direction)
        return output
    
