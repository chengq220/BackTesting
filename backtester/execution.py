from backtester.event import FillEvent
import datetime

"""
Act like the exchange
"""
class Executor():
    def __init__(self, exchange, data):
        self.exchange = exchange
        self.data = data
        self.fee = 0.01 # charging a flat fee

    """
    Executes the order events and buys/sells a tangible amount
    """
    def execute_order(self, event):

        symbol = event.symbol
        order_type = event.order_type
        dollar_quantity = event.quantity
        direction = event.direction

        symb_close_price = self.data.get_last_N_bars(symbol, 1)[-1]
        price_post_fee = symb_close_price + self.fee 
        time_index = datetime.now()

        share_quantity = dollar_quantity//price_post_fee
        commission = self.fee

        ret_event = FillEvent(timeindex=time_index,
                              symbol=symbol,
                              exchange=self.exchange,
                              quantity=share_quantity,
                              direction=direction,
                              fill_cost=symb_close_price,
                              commission=commission)
        return [ret_event]
