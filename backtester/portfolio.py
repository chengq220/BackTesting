from backtester.event import OrderEvent
from collections import defaultdict
from datetime import datetime

"""
Portfolio class to simulate one's investment portfolio
"""
class Portfolio():
    """
    Contains fields such as free_cash, equity, position, trade logs, historys
    """
    def __init__(self, inital_cash):
        self.free_cash = inital_cash # Un-invested cash
        self.equity = inital_cash # Free_cash + value of position
        self.position = defaultdict(int)
        self.trade_log = []
        self.portfolio_history = []

    # Update the equity of the portfolio on the market event
    def on_market(self, prices):
        position_value = 0
        for key in self.position:
            position_value += self.position[key] * prices[key]
        self.equity = self.free_cash +  position_value
        self.portfolio_history.append({
            "free_cash": self.free_cash,
            "equity": self.equity,
            "position": self.position,
        })

        return 1
        
    # Process the Signal Event and emit a more specific signal which is 
    # passed to the executor
    def handle_signal_event(self, event):
        sig_direction = event.direction
        symbol = event.symbol
        dt = datetime.now()
        if sig_direction == "LONG":
            direction = "BUY"
            quantity = self.free_cash
        elif sig_direction == "SHORT":
            direction = "SELL"
            quantity = self.position[symbol]
        else:
            return 
        ret_event = OrderEvent(symbol=symbol, 
                                order_type="MARKET", 
                                quantity=quantity, 
                                datetime=dt, 
                                direction=direction)
        return [ret_event]
    
    # Handles the updating for sell
    # for now sell/shorting is just going to be sell all of the assets
    # and return it to free-cash for simplicity 
    def __update_sell(self, event):
        share_sold = self.position[event.symbol]
        self.position[event.symbol] = 0
        self.free_cash = self.free_cash + event.quantity - share_sold * event.commission
        return 1

    # Handle the updating for buy
    def __update_buy(self, event):
        self.position[event.symbol] += event.quantity
        self.free_cash = self.free_cash - (event.fill_cost + event.commission) * event.quantity
        return 1
    
    # Update the portfolio to reflect the position change
    def handle_fill_event(self, event):
        if event.direction == "SELL":
            _ = self.__update_sell(event) #Flat
        elif event.direction == "BUY":
            _ = self.__update_buy(event)
        position_value = 0
        for symb in self.position:
            position_value += self.position[symb] * event.fill_cost
        self.equity = self.free_cash + position_value
        self.trade_log.append(event)
        return 1


        

