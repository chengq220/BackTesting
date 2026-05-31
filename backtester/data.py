import yfinance as yf
from backtester.event import MarketEvent, TerminateEvent

class Data:
    def __init__(self, tickers:list):
        assert type(tickers) is list, "Ticker must be a list"
        assert len(tickers) > 0, "Must be non-empty"
        self.num_tickers = len(tickers)
        self.stocks = {}
        self.__download__(tickers)

    def __download__(self, tickers:str, interval:str=None):
        for tick in tickers:
            up_tick = tick.upper()
            if interval:
                stock_info = yf.download([up_tick], auto_adjust=True, interval=interval)
            else:
                stock_info = yf.download([up_tick], auto_adjust=True)
            self.stocks[up_tick] = stock_info
        self.num_data = len(self.stocks[tickers[0].upper()])

    def get_data(self):
        return self.stocks
    
    def get_specific_stock(self, ticker:str):
        return self.stocks[ticker.upper()]

class DataHandler:
    def __init__(self, tickers:list, queue):
        self.data = Data(tickers)
        self.tickers = tickers
        self.curBar = 0
        self.q = queue

    # Since this is backtesting, we have all the historic data
    # so we can just index it    
    def updateBar(self):
        if(self.curBar >= self.data.num_data):
            self.q.append(TerminateEvent())
            return
        self.curBar += 1
        self.q.append(MarketEvent())
        return 
    
    def get_last_N_bars(self, symbol, N):
        start, end = max(0, self.curBar - N), self.curBar
        last_N = self.data.get_data()[symbol.upper()].iloc[start:end]
        return last_N


