import yfinance as yf

class Data:
    def __init__(self, tickers:str):
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

    def get_data(self):
        return self.stocks
    
    def get_specific_stock(self, ticker:str):
        return self.stocks[ticker.upper()]
    
    def metrics():
        return 0
