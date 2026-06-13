from backtester.event import SignalEvent
import time

# Answer the question "what is my directional view right now?"
class Strategy:
    def __init__(self, data_handler, inst = "MAC"):
        # The market data
        self.data = data_handler

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
        event_out = []
        for symb in self.tickers:
            symb = symb.upper()
            symb_direction = self.generate_signal(symb)
            if(symb_direction != self.direction[symb]): # Only emit signal event if we see a change in the direction
                event_out.append(symb_direction)
                self.direction[symb] = symb_direction
        return event_out

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

    return [long, short, out]
    """
    def get_signal(self, dt):
        lma_1 = dt.mean()
        sma_1 = dt[-30:].mean()
        
        lma_0 = self.lma[-1] if len(self.lma) > 0 else None
        sma_0 = self.sma[-1] if len(self.sma) > 0 else None

        self.lma.append(lma_1)
        self.sma.append(sma_1)

        if lma_0 and sma_0:
            if(lma_0 - sma_0 > 0 and lma_1 - sma_1 < 0):
                return "SHORT"
            elif(lma_0 - sma_0 < 0 and lma_1 - sma_1 > 0):
                return "LONG"
            
        return self.cur_strats
        


        
        



