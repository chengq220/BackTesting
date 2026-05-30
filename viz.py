import yfinance as yf
import matplotlib.pyplot as plt
from backtester.data import Data


if __name__ == "__main__":
    msft = Data(["msft", "aapl"])
    print(msft.get_specific_stock("AAPl"))
