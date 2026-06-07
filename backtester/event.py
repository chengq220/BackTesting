
# Base class for event types
class Event:
    def __init__(self, categ):
        self.type = categ

# Event to trigger market updates
class MarketEvent(Event):
    def __init__(self):
        super().__init__("MARKET") 

# Event to terminate back testing
class TerminateEvent(Event):
    def __init__(self):
        super().__init__("KILL") 

# Event to take into account the signal from the strategy
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

# Event to place the order for the assets
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

# Execute the trade
class FillEvent(Event):
    """
    timeindex - time the stock is filled
    symbol - ticker symbol
    exchange - from which exchange the order is filled
    quantity - the number of stocks to buy/sell
    direction - buy/sell
    fill_cost - the total cost for the order
    commission - the fee that are applied 
    """
    def __init__(self, timeindex, symbol, exchange, quantity, 
                 direction, fill_cost, commission = None):
        super().__init__("FILL") 
        self.time_index = timeindex
        self.symbol = symbol
        self.exchange = exchange
        self.quantity = quantity
        self.direction = direction
        self.fill_cost = fill_cost
        self.commission = commission if commission else 0
