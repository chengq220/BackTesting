from backtester.event import SignalEvent
from collections import defaultdict

class MAC():
    """
    Moving Average Crossover
    """
    def __init__(self, tickers, params):
        self.tickers = tickers
        self.lma = defaultdict(list)
        self.sma = defaultdict(list)
        self.sh = params["fast_sma"]
        self.lh = params["slow_sma"]
    
    # On market event, pulls the latest bars, and generate signal and add those signals back to the queue
    def on_market(self, args):
        # Generate Signal Events for each of the tickers
        event_out = []
        for symb in self.tickers:
            symb = symb.upper()
            symb_direction = self.generate_signal(symb, args['dt'], args['date'])
            event_out.append(symb_direction)
        return event_out

    # Strategy used to generate the signals
    def generate_signal(self, ticker, data, datetime):
        dt = data.get_last_N_bars(ticker, 60)
        direction = self.get_signal(ticker, dt)
        # datetime = time.time()
        output = SignalEvent(ticker, datetime, direction)
        return output

    """
    Compute the directional signal for the stock using the moving average 
    @param dt - 60 days stock ending prices

    return [long, short, hold, out]
    """
    def get_signal(self, symbol, dt):
        lma_1 = dt[-self.lh:].mean()
        sma_1 = dt[-self.sh:].mean()
        
        lma_cur = self.lma[symbol]
        sma_cur = self.sma[symbol]

        lma_0 = lma_cur[-1] if len(lma_cur) > 0 else None
        sma_0 = sma_cur[-1] if len(sma_cur) > 0 else None

        self.lma[symbol].append(lma_1)
        self.sma[symbol].append(sma_1)

        has_prev_data = lma_0 and sma_0

        return_strat = "HOLD"
        if has_prev_data:
            if(lma_0 - sma_0 > 0 and lma_1 - sma_1 < 0):
                return_strat = "SHORT"
            elif(lma_0 - sma_0 < 0 and lma_1 - sma_1 > 0):
                return_strat = "LONG"

        return return_strat
        
class DCA_LS():
    """
    Dollar Cost Averaging/Lump Sum
    """
    def __init__(self, tickers):
        self.tickers = tickers

    """
    Dollar Cost Averaging/Lump Sum Signals
    """
    def on_market(self, args):
        output = []
        datetime = args['date']
        for ticker in self.tickers:
            # datetime = time.time()
            ticker_signal = SignalEvent(ticker, datetime, "LONG")
            output.append(ticker_signal)
        return output

