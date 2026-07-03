from ollama import chat
from ollama import ChatResponse
import time
from backtester.event import SignalEvent

class LLM_Strategy():
    def __init__(self, tickers):
        self.tickers = tickers

    def on_market(self, args):
        res = []
        dt = args['dt'] # stock data
        for tick in self.tickers:
            direction = self.generate_signal(tick, dt)
            datetime = time.time()
            output = SignalEvent(tick, datetime, direction)
            res.append(output)
        return res

    def generate_signal(self, symbol, data, horizon=60):
        dt = data.get_last_N_bars(symbol, horizon)
        dt_processed = ",".join([f"({idx-horizon+1}, {dt[idx].item()})" for idx in range(dt.shape[0])])
        response: ChatResponse = chat(model='gemma3:1b', messages=[
        {
            'role': 'user',
            'content': f'''You are a quantitative trading signal generator.
                Given the following stock price sequence over {horizon} days in the format 
                (x, y) where x is the number of days prior and y is the price at x:
                {dt_processed}

                Analyze the trend, momentum, and recent price action.
                If the trend is clearly upward → LONG
                If the trend is clearly downward → SHORT  
                If the trend is unclear or sideways → HOLD
                If you have no conviction → OUT

                Return exactly one word: LONG, SHORT, HOLD, or OUT'''
        },
        ])
        signal = (response.message.content).strip().upper()

        # Hallucination safety guardrail
        if signal not in ["HOLD", "LONG", "SHORT", "OUT"]:
            signal = "HOLD"
        return signal

