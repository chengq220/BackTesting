from backtester.event import SignalEvent
import time

# Answer the question "what is my directional view right now?"
class Strategy:
    def __init__(self, data_handler, queue, inst = "MAC"):
        # The market data
        self.data = data_handler

        # The action queue 
        self.q = queue

        # The company tickers we are tracking
        self.tickers = self.data.tickers

        # The strategy used for the signal
        if(inst == "MAC"):
            self.strats = MAC()
        elif(inst == "NN"):
            self.strats = None
        else:
            raise NotImplementedError

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
    def generate_signal(self, ticker):
        dt = self.data.get_last_N_bars(ticker, 60)
        direction = self.strats.get_signal(dt)
        datetime = time.time()
        output = SignalEvent(ticker, datetime, direction)
        return output
    
class MAC():
    def __init__(self):
        self.lma = []
        self.sma = []
        self.cur_strats = "OUT"
    
    """
    Compute the directional signal for the stock using the moving average 
    @param dt - 60 days stock ending prices

    return [long, short, out (stay)]
    """
    def get_signal(self, dt):
        if len(self.lma) == 0:
            return "OUT"
        
        lma_1 = dt["Close"].mean().iloc[0]
        sma_1 = dt["Close"][-30:].mean().iloc[0]
        
        lma_0 = self.lma[-1]
        sma_0 = self.sma[-1]

        self.lma.append(lma_1)
        self.sma.append(sma_1)

        if(lma_0 > sma_0 and lma_1 < sma_1):
            self.cur_strats = "SHORT"
            return "SHORT"
        elif(lma_0 < sma_0 and lma_1 > sma_1):
            self.cur_strats = "LONG"
            return "LONG"
        else:
            return self.cur_strats


        
        



