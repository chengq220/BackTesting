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
        """
        Returns the total stock amount that was sold
        """
        # want to make sure that all shares are whole numbers for simplicity
        if quantity_type == 0: # cash 
            share_quantity = event.quantity // (close_price + self.fee)
        else: # stocks
            share_quantity = event.quantity
        return share_quantity
    
    # Responsible to respond to buy orders
    def __buy_order(self, event, close_price, quantity_type):
        """
        Returns the total stock amount that was bought
        """
        
        if quantity_type == 0: #cash 
            dollar_quantity = event.quantity
            price_post_fee = close_price + self.fee 
            share_quantity = dollar_quantity//price_post_fee
        else: # stocks (exiting out of a short)
            share_quantity = event.quantity

        return share_quantity

    """
    Executes the order events and buys/sells a tangible amount
    """
    def execute_order(self, event, cur_date):
        symbol = event.symbol
        order_type = event.order_type
        direction = event.direction

        # flag for whether the amount is cash or stocks shares
        quantity_type = event.quant_type
        
        symb_close_price = self.data.get_last_N_bars(symbol, 1)[-1].item()
        time_index = cur_date

        if direction == "BUY" or direction == "COVER":
            # Amount will be in terms of cash
            share_quantity = self.__buy_order(event, symb_close_price, quantity_type)
        else:
            # Amount will be in terms of cash
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
