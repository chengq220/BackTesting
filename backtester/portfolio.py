from backtester.event import OrderEvent
from collections import defaultdict
from datetime import datetime

"""
Portfolio class to simulate one's investment portfolio
"""
class Portfolio():
    """
    Contains fields such as free_cash, equity, position, trade logs, historys
    parameters:
    initial_cash - the starting capital
    sizing_rule - how much are invested each time a investment is made
    frequency - how often are investment signal getting send (in days)
    """
    def __init__(self, inital_cash, sizing_rule = "10000", frequency = 1):
        self.free_cash = inital_cash # Un-invested cash
        self.equity = inital_cash # Free_cash + value of position
        if sizing_rule.isnumeric():
            self.sizing_rule = int(sizing_rule)
            
        else:
            self.sizing_rule = None
        self.frequency = frequency
        self.position = defaultdict(int)
        self.trade_log = []
        self.portfolio_history = []
        self.last_buy = 0

    # Update the equity in the portfolio on the market event
    def on_market(self, prices):
        position_value = 0
        for key in self.position:
            position_value += self.position[key] * prices[key]
        self.equity = self.free_cash + position_value
        self.portfolio_history.append({
            "free_cash": self.free_cash,
            "equity": self.equity,
            "position": self.position.copy(),
        })

        return 1
        
    # Process the Signal Event and emit a more specific signal which is 
    # passed to the executor
    # Don't have to check if we have enough money because we only send the order in dollar amount for buy
    # and also share amount for sell. Therefore, no complex checking need to be done
    def handle_signal_event(self, event):
        # only buy according to the frequency
        ret_event = None
        if self.last_buy % self.frequency == 0: 
            sig_direction = event.direction
            symbol = event.symbol
            dt = datetime.now()
            if sig_direction == "LONG":
                direction = "BUY"
                quantity = self.__compute_buy_quantity()
            elif sig_direction == "SHORT":
                direction = "SELL"
                quantity = self.position[symbol]
            else:
                return []
            ret_event = OrderEvent(symbol=symbol, 
                                    order_type="MARKET", 
                                    quantity=quantity, 
                                    datetime=dt, 
                                    direction=direction)

        # Update last buy
        self.last_buy += (self.last_buy + 1) % self.frequency
        if ret_event and ret_event.quantity > 0:
            return [ret_event]
        return []

    # Different ways to identify sizing of the quantity for buying
    def __compute_buy_quantity(self):
        if self.sizing_rule:
            if self.free_cash < 1.0: # each available trade must have value > $1
                return 0
            if self.free_cash < self.sizing_rule:
                return self.free_cash
            return self.sizing_rule
        else:
            return 0
    
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


        

