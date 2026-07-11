from backtester.strategies.classic import *
from backtester.strategies.llm_strategy import *

# Answer the question "what is my directional view right now?"
class StrategyContainer:
    def __init__(self, data_handler, strat_dict:dict):
        # The market data
        self.data = data_handler

        # The company tickers we are tracking
        self.tickers = self.data.tickers

        strategy = strat_dict["strategy"]
        params = strat_dict["strategy_param"]

        # The strategy used for the signal
        if(strategy == "MAC"):
            self.strats = MAC(self.tickers, params)
        elif(strategy == "DCA" or strategy == "LS"):
            self.strats = DCA_LS(self.tickers)
        elif(strategy == "LLM"):
            self.strats = LLM_Strategy(self.tickers)
        elif(strategy == "NN"):
            self.strats = None
        else:
            raise NotImplementedError

    # Retrieve the response to a on-market signal for each strategy
    def on_market(self, cur_date):
        return self.strats.on_market({
            'date': cur_date,
            'dt': self.data
        })
            

        
        



