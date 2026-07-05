import yfinance as yf
from event import MarketEvent, TerminateEvent
# from backtester.event import MarketEvent, TerminateEvent
from collections import deque

class Data:
    def __init__(self, tickers:list, start:str, end:str):
        assert type(tickers) is list, "Ticker must be a list"
        assert len(tickers) > 0, "Must be non-empty"
        self.num_tickers = len(tickers)
        self.stocks = {}
        self.__download__(tickers, start, end)

    def __download__(self, tickers:str, start, end):
        for tick in tickers:
            stock_info = yf.download([tick], auto_adjust=True, start=start, end=end, interval="1d")
            self.stocks[tick] = stock_info
        self.num_data = len(self.stocks[tickers[0]])

    def get_data(self):
        return self.stocks
    
    def get_specific_stock(self, ticker:str):
        return self.stocks[ticker.upper()]

class DataHandler:
    def __init__(self, tickers:list, start:str, end:str, curBar:int=60):
        self.data = Data(tickers, start, end)
        self.tickers = tickers
        for idx, tick in enumerate(self.tickers):
            self.tickers[idx] = tick.upper()
        self.curBar = curBar if curBar else 0

    def get_current_day(self):
        return self.data.get_data()[self.tickers.keys()[0]].iloc[self.curBar]["Date"][0]

    # Since this is backtesting, we have all the historic data
    # so we can just index it    
    def updateBar(self):
        if(self.curBar >= self.data.num_data):
            return [TerminateEvent()]
        self.curBar += 1
        return [MarketEvent()]
    
    #get up to the past 60 days of data 
    def get_last_N_bars(self, symbol, N):
        start, end = max(0, self.curBar - N), self.curBar
        last_N = self.data.get_data()[symbol].iloc[start:end]["Close"].to_numpy()
        return last_N


if __name__ == "__main__":
    # from collections import deque
    # queue = deque()
    # data = DataHandler(["ivv"])
    # stk_price = data.get_last_N_bars("ivv", 2)
    # print(stk_price)

    amazon_weekly= yf.download(["amzn"], start="2009-12-01", end="2010-2-12", interval="1d", auto_adjust=True)
    print(amazon_weekly)
