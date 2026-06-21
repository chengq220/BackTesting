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
    def __sell_order(self, event, close_price, quantity_type):
        # want to make sure that all shares are whole numbers for simplicity
        if quantity_type == 0: # cash 
            share_quantity = event.quantity // (close_price + self.fee)
        else: # stocks
            share_quantity = event.quantity

        total_value = share_quantity * close_price
        return total_value
    
    # Responsible to respond to buy orders
    def __buy_order(self, event, close_price, quantity_type):
        if quantity_type == 0: #cash 
            dollar_quantity = event.quantity
            price_post_fee = close_price + self.fee 
            share_quantity = dollar_quantity//price_post_fee
            
            total_bought = share_quantity * close_price
        else: # stocks (exiting out of a short)
            stock_quantity = event.quantity
            total_bought = stock_quantity * close_price
        return total_bought

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

        if direction == "BUY" or direction == "COVER":
            share_quantity = self.__buy_order(event, symb_close_price, quantity_type)
        else:
            share_quantity = self.__sell_order(event, symb_close_price, quantity_type)
        
        commission = self.fee
        ret_event = FillEvent(timeindex=time_index,
                              symbol=symbol,
                              exchange=self.exchange,
                              quantity=share_quantity,
                              direction=direction,
                              fill_cost=symb_close_price,
                              commission=commission)
        return [ret_event]
