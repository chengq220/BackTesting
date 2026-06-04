from backtester.event import OrderEvent
class Portfolio():
    def __init__(self, inital_cash = 10000):
        self.free_cash = inital_cash
        self.position = {}
        self.trade_log = []
        self.portfolio_history = []
        
    def handle_signal(self, event):
        return 0
