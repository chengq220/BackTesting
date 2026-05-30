
# Base class for event types
class Event:
    def __init__(self, categ):
        self.type = categ

# 
class MarketEvent(Event):
    def __init__(self):
        super().__init__("MARKET") 

# 
class SignalEvent(Event):
    """
    symbol - ticker symbol
    datetime - the time stamp for the signal
    direction - short/long
    """
    def __init__(self, symbol, datetime, direction):
        super().__init__("SIGNAL") 
        self.symbol = symbol
        self.datetime = datetime
        self.direction = direction

#
class OrderEvent(Event):
    """
    symbol - ticker symbol
    datetime - the time stamp for the signal
    direction - buy/sell
    order_type - market or limit
    quantity - the number of stocks to buy/sell
    """
    def __init__(self, symbol, datetime, direction, order_type, quantity):
        super().__init__("ORDER") 
        self.symbol = symbol
        self.order_type = order_type
        self.quantity = quantity
        self.datetime = datetime
        self.direction = direction

    def print_order(self):
        """
        Outputs the values within the Order.
        """
        print("At time%s , Order: Symbol=%s, Type=%s, Quantity=%s, Direction=%s" % \
            (self.datetime, self.symbol, self.order_type, self.quantity, self.direction))

# 
class FillEvent(Event):
    def __init__(self, timeindex, symbol, exchange, quantity, 
                 direction, fill_cost, commission=None):
        super().__init__("FILL") 
        self.time_index = timeindex
        self.symbol = symbol
        self.exchange = exchange
        self.quantity = quantity
        self.direction = direction
        self.fill_cost = fill_cost
        
        self.commission = 0 if not commission else self.compute_coommision()

    def compute_coommision(self):
        full_cost = 1.3
        if self.quantity <= 500:
            full_cost = max(1.3, 0.013 * self.quantity)
        else: # Greater than 500
            full_cost = max(1.3, 0.008 * self.quantity)
        full_cost = min(full_cost, 0.5 / 100.0 * self.quantity * self.fill_cost)
        return full_cost
