import yfinance as yf

class Data:
    def __init__(self, tickers:str):
        assert type(tickers) is list, "Ticker must be a list"
        assert len(tickers) > 0, "Must be non-empty"
        self.num_tickers = len(tickers)
        self.dat = yf.download(tickers, auto_adjust=True)

    def get_data(self):
        return self.dat
