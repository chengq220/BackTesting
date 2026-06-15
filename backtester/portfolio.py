from backtester.event import OrderEvent
from collections import defaultdict
from datetime import datetime


POSITION_INDICES = {0:"SHORT", 1:"OUT", 2:"LONG"}

"""
Portfolio class to simulate one's investment portfolio
"""
class Portfolio():
    """
    Contains fields such as free_cash, equity, inventory, trade logs, historys
    parameters:
    initial_cash - the starting capital
    sizing_rule - how much are invested each time a investment is made
    frequency - how often are investment signal getting send (in days)
    """
    def __init__(self, inital_cash, sizing_rule = "10000", frequency = 1):
        self.free_cash = inital_cash # liquid cash
        self.equity = inital_cash # Free_cash + value of inventory
        if sizing_rule.isnumeric():
            self.sizing_rule = int(sizing_rule)
            
        else:
            self.sizing_rule = None
        self.frequency = frequency
        self.position = defaultdict(lambda: 1) # Position all starts with 2 which corresponds to OUT
        self.inventory = defaultdict(int) # Number of stocks you are holding
        self.trade_log = []
        self.portfolio_history = []
        self.last_buy = 0
        self.pending = None

    # Update the equity in the portfolio on the market event
    def on_market(self, prices):
        inventory_value = 0
        for key in self.inventory:
            inventory_value += self.inventory[key] * prices[key]
        self.equity = self.free_cash + inventory_value
        self.portfolio_history.append({
            "free_cash": self.free_cash,
            "equity": self.equity,
            "inventory": self.inventory.copy(),
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
            dt = datetime.now()
            position_change = event.direction == self.position[event.symbol]
            # regardless of the positoin, the main functions are the same except for how they are handled
            # and how many time the signals are emitted for position changed from short -> long and long -> short
            if position_change: 
                if event.direction == "LONG":
                    direction = "BUY"
                    quantity = self.__compute_buy_quantity()
                elif event.direction == "SHORT":
                    direction = "SELL"
                    quantity = self.__compute_sell_quantity(event.symbol)
            else:
                return []
            ret_event = OrderEvent(symbol=event.symbol, 
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
        
    def __compute_sell_quantity(self, symbol):
        # For simplicity, when buying back owed stocks in shorting
        # this backtester assume you have to return all not just partially 
        return self.inventory[symbol]
    
    # Handles the updating for sell
    # for now sell/shorting is just going to be sell all of the assets
    # and return it to free-cash for simplicity 
    def __update_sell(self, event):
        share_sold = self.inventory[event.symbol]
        self.inventory[event.symbol] = 0
        self.free_cash = self.free_cash + event.quantity - share_sold * event.commission
        return 1

    # Handle the updating for buy
    def __update_buy(self, event):
        self.inventory[event.symbol] += event.quantity
        self.free_cash = self.free_cash - (event.fill_cost + event.commission) * event.quantity
        return 1
    
    # Update the portfolio to reflect the position change
    def handle_fill_event(self, event):
        if event.direction == "SELL":
            self.position[event.symbol] -= min(0, self.position[event.symbol]-1)
            _ = self.__update_sell(event) # Flat
        elif event.direction == "BUY":
            self.position[event.symbol] += max(2, self.position[event.symbol]+1)
            _ = self.__update_buy(event)
        inventory_value = 0
        for symb in self.inventory:
            inventory_value += self.inventory[symb] * event.fill_cost
        self.equity = self.free_cash + inventory_value
        self.trade_log.append(event)
        
        # If there is another step that needs to be taken
        if self.pending:
            dt = datetime.now()
            direction = self.pending
            quantity = self.__compute_buy_quantity() if direction else self.__compute_sell_quantity(event.symbol)
            self.pending = None
            return [OrderEvent(symbol=event.symbol, 
                                    order_type="MARKET", 
                                    quantity=quantity, 
                                    datetime=dt, 
                                    direction=direction)]
        return 1


        

