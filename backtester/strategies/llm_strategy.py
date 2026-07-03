from ollama import chat
from ollama import ChatResponse

class LLM_Strategy():
    def __init__(self, tickers):
        self.tickers = tickers

    def on_market(self, args):
        res = []
        dt = args['dt'] # stock data
        for tick in self.tickers:
            res.append(self.generate_signal(tick, dt))
        return res

    def generate_signal(self, symbol, data, horizon=60):
        dt = data.get_last_N_bars(symbol, horizon)
        dt_processed = ",".join([f"({idx-horizon+1}, {dt[idx].item()})" for idx in range(dt.shape[0])])
        response: ChatResponse = chat(model='gemma3:1b', messages=[
        {
            'role': 'user',
            'content': f'Instruction: You are a strict financial advisor on what position should be taken for certain stocks. \
            Prompt: Given the stock price data {dt_processed}, what should the position be? Choose and return 1 option from\
                from the following: LONG, SHORT, HOLD, OUT. ONLY returb the position as there is no need for explanation.',
        },
        ])
        signal = (response.message.content).upper()

        # Hallucination safety guardrail
        if signal not in ["HOLD", "LONG", "SHORT", "OUT"]:
            signal = "HOLD"
        return signal


# if __name__ == "__main__":

