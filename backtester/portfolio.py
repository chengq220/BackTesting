from backtester.event import OrderEvent
from collections import defaultdict
from datetime import datetime

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
    def __init__(self, inital_cash, sizing_rule = 2000, frequency = 5):
        self.free_cash = defaultdict(lambda: inital_cash)

        # all stocks : (Free_cash + value of inventory)
        self.equity = 0 # Not initailized yet, empty portfolio at initialization

        # How much to invest when adding a position
        self.sizing_rule = sizing_rule 
        # How many days before adding more money to a position
        self.invest_frequency = frequency

        # {"SHORT", "OUT", "LONG", "HOLD"}
        # Assume that at any time, we are only at 1 position for any stock
        self.position = defaultdict(lambda: "OUT") # Position all starts "OUT"
        self.inventory = defaultdict(lambda: 0) # Number of stocks you are holding

        self.trade_log = []
        self.portfolio_history = []

        # last time each position changed
        self.last_change_pos = defaultdict(lambda: 1)

        # Logic: from long to short : sell position -> out -> sell position
        # Logic from short to long : buy position that's owed -> out -> buy position
        # Possible states: "None", "BUY", "SHORT"
        self.pending = None

    # Initialize the portfolio with the stocks info that we want to look at
    def init_portfolio(self, tickers):
        for tick in tickers:
            self.position[tick]
            self.inventory[tick]
            self.free_cash[tick]
        return 1

    # Update the equity in the portfolio on the market event
    def on_market(self, prices):
        """
        Update the value of the portfolio based on everyday update
        """
        inventory_value = 0
        left_over_cash = 0
        for key in self.inventory:
            inventory_value += self.inventory[key] * prices[key]
            left_over_cash += self.free_cash[key]
        self.equity = left_over_cash + inventory_value
        self.portfolio_history.append({
            'free_cash': left_over_cash,
            "equity": self.equity,
            "inventory": self.inventory.copy(),
            "position": self.position.copy()
        })

        return 1
    
    # Different ways to identify sizing of the quantity for buying
    def __compute_buy_quantity(self, symbol, direction = "BUY"):
        """
        return (x, y) where x is the amount and y is whether it is a share/dollar amount
        """
        if direction == "BUY": # If in buy, the quantity is in dollar 
            if self.sizing_rule: 
                if self.free_cash[symbol] < 1.0: # each available trade must have value > $1
                    return 0, 0 
                if self.free_cash[symbol] < self.sizing_rule:
                    return self.free_cash[symbol], 0
                return self.sizing_rule, 0
            else:
                return 0, 0
        elif direction == "COVER": # If in cover the quantity is in stocks
            return abs(self.inventory[symbol]), 1
        else:
            print("You are not suppose to be here!")
            raise NotImplementedError

        
    def __compute_sell_quantity(self, symbol, direction = "SELL"):
        # For simplicity, when buying back owed stocks in shorting
        # this backtester assume you have to return all not just partially 
        if direction == "SELL": # if in sell, quantity is the # of stocks
            return self.inventory[symbol], 1 # Number of stocks
        elif direction == "SHORT": # If shorting, the quantity is the total amount in dollar to short (fixed amount)
            return self.sizing_rule, 0
        else:
            print("You are not suppose to be here!")
            raise NotImplementedError
        
    # Process the Signal Event and emit a more specific signal which is 
    # passed to the executor
    # Don't have to check if we have enough money because we only send the order in dollar amount for buy
    # and also share amount for sell. Therefore, no complex checking need to be done
    def handle_signal_event(self, event):
        # only buy according to the frequency
        if self.last_change_pos[event.symbol] < self.invest_frequency:
            ret_event = None
        else:
 
            dt = datetime.now()
            position_change = event.direction != self.position[event.symbol]
            direction = "HOLD" if self.position[event.symbol] != "OUT" else "OUT"
            quantity, quantity_type = 0, 0
            
            # regardless of the position, the main functions are the same except for how they are handled
            # and how many time the signals are emitted for position changed
            # SHORT -> LONG or LONG -> SHORT, could also be OUT -> LONG or OUT -> SHORT
            isOut = self.position[event.symbol] == "OUT"
            if isOut:
                if event.direction == "LONG":
                    direction = "BUY" # when exiting out of a short position, if not enough money, go into debt
                    quantity, quantity_type = self.__compute_buy_quantity(event.symbol, direction)
                    self.last_change_pos[event.symbol] = 0
                elif event.direction == "SHORT": 
                    direction = "SHORT"
                    quantity, quantity_type = self.__compute_sell_quantity(event.symbol, direction)
                    self.last_change_pos[event.symbol] = 0
                elif event.direction == "HOLD" or event.direction == "OUT":
                    direction = self.position[event.symbol] # Maintain current position
                self.pending = None

            if not isOut and position_change: 
                if event.direction == "LONG":
                    direction = "COVER" # when exiting out of a short position, if not enough money, go into debt
                    quantity, quantity_type = self.__compute_buy_quantity(event.symbol, direction)
                    self.pending = "BUY"
                    self.last_change_pos[event.symbol] = 0
                elif event.direction == "SHORT": # 
                    direction = "SELL"
                    quantity, quantity_type = self.__compute_sell_quantity(event.symbol, direction)
                    self.pending = "SHORT"
                    self.last_change_pos[event.symbol] = 0
                elif event.direction == "HOLD":
                    direction = self.position[event.symbol] # Maintain current position
                    self.pending = None
                elif event.direction == "OUT": # when just trying to exit
                    if self.position[event.symbol] == "LONG":
                        direction = "SELL"
                        quantity, quantity_type = self.__compute_sell_quantity(event.symbol, direction)

                    elif self.position[event.symbol] == "SHORT":
                        direction = "COVER"
                        quantity, quantity_type = self.__compute_buy_quantity(event.symbol, direction)
                    self.last_change_pos[event.symbol] = 0
                    self.pending = None

            # If we stay at some position for some amount of time 
            # and we still ahve cash, just put more into the position
            if not position_change:
                if event.direction == "LONG":
                    direction = "BUY" # when exiting out of a short position, if not enough money, go into debt
                    quantity, quantity_type = self.__compute_buy_quantity(event.symbol, direction)
                    self.last_change_pos[event.symbol] = 0
                elif event.direction == "SHORT": 
                    direction = "SHORT"
                    quantity, quantity_type = self.__compute_sell_quantity(event.symbol, direction)
                    self.last_change_pos[event.symbol] = 0
                elif event.direction == "HOLD" or event.direction == "OUT":
                    direction = self.position[event.symbol] # Maintain current position
                self.pending = None

            # If position did not change, just continue with the same position
            ret_event = OrderEvent(symbol=event.symbol, 
                                    order_type="MARKET", 
                                    quantity=quantity, 
                                    datetime=dt, 
                                    direction=direction,
                                    quant_type=quantity_type)
            
        # Update last buy for the particular stock
        self.last_change_pos[event.symbol] += 1
        if ret_event:
            if ret_event.quantity > 0:
                return [ret_event]
        
        return []
    
    def __update_position_inv(self, event):
        """
        Event quantity is all in terms of stock quantity regardless of buy/sell since it is consolidated
        in the executor to all stock quantity
        Based on the direction, update the position of the inventory
        """

        shares = event.quantity 

        if event.direction == "SHORT": # need to be in out/short position to short (essentially same as selling)
            self.position[event.symbol] = "SHORT"
            self.inventory[event.symbol] -= shares
            self.free_cash[event.symbol] += shares * (event.fill_cost - event.commission)

        elif event.direction == "SELL": # Need to be in long position to sell 
            self.position[event.symbol] = "OUT"
            self.inventory[event.symbol] -= shares
            self.free_cash[event.symbol] += shares * (event.fill_cost -  event.commission)
        
        elif event.direction == "COVER": # need to be in the short position to cover (essentially same as buying)
            self.position[event.symbol] = "OUT"
            self.inventory[event.symbol] += shares
            self.free_cash[event.symbol] -= shares * (event.fill_cost + event.commission)

        elif event.direction == "BUY": # need to be in out position/long position to buy
            self.position[event.symbol] = "LONG"
            self.inventory[event.symbol] += shares
            self.free_cash[event.symbol] -=  shares * (event.fill_cost +  event.commission)

        inventory_value = 0
        inventory_value += self.inventory[event.symbol] * event.fill_cost

    # Update the portfolio to reflect the position change
    def handle_fill_event(self, event):
        """
        Update the portfolio position
        """
        self.__update_position_inv(event)
        # If there is another step that needs to be taken
        if self.pending:
            dt = datetime.now()
            if self.pending == "BUY":
                quantity, quantity_type  = self.__compute_buy_quantity(event.symbol, self.pending)
            elif self.pending == "SHORT":
                quantity, quantity_type = self.__compute_sell_quantity(event.symbol, self.pending)
            if quantity > 0:
                pending_order = [OrderEvent(symbol=event.symbol, 
                                            order_type="MARKET", 
                                            quantity=quantity, 
                                            datetime=dt, 
                                            direction=self.pending,
                                            quant_type=quantity_type)]
                self.last_change_pos[event.symbol] = 0
                self.pending = None
                return pending_order
            else:
                self.pending = None
        return None
    
    # Liquidate the portfolio
    def exit_position(self):
        ret_events = []
        for tick in self.position.keys():
            cur_position = self.position[tick]
            cur_order = None
            if cur_position == "LONG":
                direction = "SELL"
                quantity, quantity_type = self.__compute_sell_quantity(tick, "SELL")
                cur_order = OrderEvent(symbol=tick, 
                    order_type="MARKET", 
                    quantity=quantity, 
                    datetime=dt, 
                    direction=direction,
                    quant_type=quantity_type)
            elif cur_position == "SHORT":
                direction = "COVER"
                quantity, quantity_type = self.__compute_buy_quantity(tick, "COVER")
                dt = datetime.now()
                cur_order = OrderEvent(symbol=tick, 
                            order_type="MARKET", 
                            quantity=quantity, 
                            datetime=dt, 
                            direction=direction,
                            quant_type=quantity_type)
            if cur_order:
                ret_events.append(cur_order)
        if len(ret_events) > 0:
            return ret_events
        return []

