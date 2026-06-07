from backtester.event import OrderEvent
from collections import defaultdict
from datetime import datetime
from execution import Executor

"""
Portfolio class to simulate one's investment portfolio
"""
class Portfolio():
    """
    Contains fields such as free_cash, equity, position, trade logs, historys
    """
    def __init__(self, inital_cash, data):
        self.free_cash = inital_cash
        self.data = data
        self.equity = 0
        self.position = defaultdict(int)
        self.trade_log = []
        self.portfolio_history = []
        
    # Process the Signal Event and emit a more specific signal which is 
    # passed to the executor
    def handle_signal_event(self, event):
        sig_direction = event.direction
        symbol = event.symbol
        latest_price = self.data.get_last_N_bars(symbol, 1)["Close"][-1]
        quantity = self.free_cash // latest_price
        dt = datetime.now()
        if sig_direction == "LONG":
            direction = "BUY"
        elif sig_direction == "SHORT":
            direction = "SELL"
        else:
            return 
        ret_event = OrderEvent(symbol=symbol, 
                                order_type="MARKET", 
                                quantity=quantity, 
                                datetime=dt, 
                                direction=direction)
        return [ret_event]
    
    # Update the portfolio to reflect the position change
    def handle_fill_event(self, event):
        quantity = -1 * event.quantity if event.direction == "SELL" else event.quantity
        self.position[event.symbol] += quantity

        self.free_cash = self.free_cash - event.commission
        self.free_cash = self.free_cash - (quantity * event.fill_cost)
        self.equity = self.equit + (event.fill_cost * quantity)
        
        self.trade_log.append(event)

        self.portfolio_history.append({
            "free_cash": self.free_cash,
            "equity": self.equity,
            "position": self.position,
        })

        return 1


        

