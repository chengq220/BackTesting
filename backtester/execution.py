from backtester.event import FillEvent
import datetime

"""
Act like an exchange and fills the order event
"""
class Executor():
    def __init__(self, exchange, data, has_fee=True):
        self.exchange = exchange
        self.data = data
        self.fee = 0.01 if has_fee else 0 # charging a flat fee
    
    # Responsible to respond to sell orders
    def __sell_order(self, event, close_price):
        share_quantity = event.quantity
        total_value = share_quantity * close_price
        return total_value
    
    # Responsible to respond to buy orders
    def __buy_order(self, event, close_price):
        dollar_quantity = event.quantity
        price_post_fee = close_price + self.fee 
        share_quantity = dollar_quantity/price_post_fee
        return share_quantity

    """
    Executes the order events and buys/sells a tangible amount
    """
    def execute_order(self, event):
        symbol = event.symbol
        order_type = event.order_type
        direction = event.direction
        quantity_type = event.type
        
        symb_close_price = self.data.get_last_N_bars(symbol, 1)[-1].item()
        time_index = datetime.datetime.now()

        share_quantity = self.__buy_order(event, symb_close_price, quantity_type) if direction == "BUY" else self.__sell_order(event, symb_close_price, quantity_type)
        commission = self.fee
        
        ret_event = FillEvent(timeindex=time_index,
                              symbol=symbol,
                              exchange=self.exchange,
                              quantity=share_quantity,
                              direction=direction,
                              fill_cost=symb_close_price,
                              commission=commission)
        return [ret_event]
