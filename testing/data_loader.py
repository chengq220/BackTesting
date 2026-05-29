import yfinance as yf
import pandas as pd
import numpy as np
import pydantic


if __name__ == "__main__":
    dat = yf.Ticker("MSFT")
    dat.info
    dat.calendar
    dat.analyst_price_targets
    dat.quarterly_income_stmt
    dat.history(period='1mo')
    dat.option_chain(dat.options[0]).calls
    print(dat.option_chain(dat.options[0]).calls)
    print(type(dat))
