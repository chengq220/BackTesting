import yfinance as yf
import matplotlib.pyplot as plt
from backtester.data import Data, DataHandler


if __name__ == "__main__":
    stocks = DataHandler(["msft", "aapl"])
    print(stocks.updateBar().type)
    print(stocks.get_last_N_bars("MSFT", 5))
