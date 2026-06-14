from backtester.strategies import *

# Answer the question "what is my directional view right now?"
class StrategyContainer:
    def __init__(self, data_handler, inst = "MAC"):
        # The market data
        self.data = data_handler

        # The company tickers we are tracking
        self.tickers = self.data.tickers

        # The strategy used for the signal
        if(inst == "MAC"):
            self.strats = MAC(self.tickers)
        elif(inst == "DAC" or inst == "LS"):
            self.strats = DCA_LS(self.tickers)
        elif(inst == "NN"):
            self.strats = None
        else:
            raise NotImplementedError

    # Retrieve the response to a on-market signal for each strategy
    def on_market(self):
        return self.strats.on_market({
            'dt': self.data
        })
            

        
        



