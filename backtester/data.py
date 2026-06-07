import yfinance as yf
from backtester.event import MarketEvent, TerminateEvent
from collections import deque
# from event import MarketEvent, TerminateEvent

class Data:
    def __init__(self, tickers:list, period:str="6mo"):
        assert type(tickers) is list, "Ticker must be a list"
        assert len(tickers) > 0, "Must be non-empty"
        self.num_tickers = len(tickers)
        self.stocks = {}
        self.__download__(tickers, period)

    def __download__(self, tickers:str, period):
        for tick in tickers:
            up_tick = tick.upper()
            if period:
                stock_info = yf.download([up_tick], auto_adjust=True, period=period)
            else:
                stock_info = yf.download([up_tick], auto_adjust=True)
            self.stocks[up_tick] = stock_info
        self.num_data = len(self.stocks[tickers[0].upper()])

    def get_data(self):
        return self.stocks
    
    def get_specific_stock(self, ticker:str):
        return self.stocks[ticker.upper()]

class DataHandler:
    def __init__(self, tickers:list, period:str="1y", curBar:int=60):
        self.data = Data(tickers, period)
        self.tickers = tickers
        self.curBar = curBar if curBar else 0

    # Since this is backtesting, we have all the historic data
    # so we can just index it    
    def updateBar(self):
        if(self.curBar >= self.data.num_data):
            return [TerminateEvent()]
        self.curBar += 1
        return [MarketEvent()]
         
    
    def get_last_N_bars(self, symbol, N):
        start, end = max(0, self.curBar - N), self.curBar
        last_N = self.data.get_data()[symbol.upper()].iloc[start:end]
        return last_N


if __name__ == "__main__":
    from collections import deque
    queue = deque()
    sim = DataHandler(["aapl", "msft"], queue)
