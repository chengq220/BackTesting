import yfinance as yf
# from event import MarketEvent, TerminateEvent
from backtester.event import MarketEvent, TerminateEvent
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
            stock_info.columns = stock_info.columns.get_level_values(0)
            stock_info = stock_info.reset_index()
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
        date = self.data.get_data()[self.tickers[0]][self.curBar:self.curBar+1]["Date"]
        return date

    # Since this is backtesting, we have all the historic data
    # so we can just index it    
    def updateBar(self):
        print(self.curBar)
        print(self.data.num_data)
        print("===================================")
        if(self.curBar >= self.data.num_data):
            return [TerminateEvent()]
        
        res_event = [MarketEvent()]
        self.curBar += 1
        return res_event
    
    #get up to the past 60 days of data 
    def get_last_N_bars(self, symbol, N):
        start, end = max(0, self.curBar - N), self.curBar
        last_N = self.data.get_data()[symbol][start:end]["Close"].to_numpy()
        return last_N

# if __name__ == "__main__":
#     # from collections import deque
#     # queue = deque()
#     # data = DataHandler(["ivv"])
#     # stk_price = data.get_last_N_bars("ivv", 2)
#     # print(stk_price)

#     # amazon_weekly= yf.download(["amzn"], start="2009-12-01", end="2010-4-12", interval="1d", auto_adjust=True)
#     # print(amazon_weekly)
