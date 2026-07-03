from backtester.strategies.classic import *
from backtester.strategies.llm_strategy import *

# Answer the question "what is my directional view right now?"
class StrategyContainer:
    def __init__(self, data_handler, strat = "MAC"):
        # The market data
        self.data = data_handler

        # The company tickers we are tracking
        self.tickers = self.data.tickers

        # The strategy used for the signal
        if(strat == "MAC"):
            self.strats = MAC(self.tickers)
        elif(strat == "DCA" or strat == "LS"):
            self.strats = DCA_LS(self.tickers)
        elif(strat == "LLM"):
            self.strats = LLM_Strategy(self.tickers)
        elif(strat == "NN"):
            self.strats = None
        else:
            raise NotImplementedError

    # Retrieve the response to a on-market signal for each strategy
    def on_market(self):
        return self.strats.on_market({
            'dt': self.data
        })
            

        
        



