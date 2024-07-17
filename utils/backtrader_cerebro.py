import backtrader as bt
from errors_handler.decorator import error_tracking_decorator
import matplotlib

# better net liquidation value view
class MyBuySell(bt.observers.BuySell):
    plotlines = dict(
        buy=dict(marker='$\u21E7$', markersize=12.0),
        sell=dict(marker='$\u21E9$', markersize=12.0)
    )

class CelebroCreator:
    def __init__(self, strategy=None, list_of_data=None, stake=100, cash=20000):
        self.cerebro = bt.Cerebro(cheat_on_open=True)

        if strategy:
            self.cerebro.addstrategy(strategy)
        self.cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='SharpeRatio')
        self.cerebro.addanalyzer(bt.analyzers.Returns, _name='Returns')
        self.cerebro.addobserver(bt.observers.Value)

        for data in list_of_data:
            self.cerebro.adddata(data)
        self.cerebro.broker.set_cash(cash)
        bt.observers.BuySell = MyBuySell
        
        self.strats = None
        _, self.message = self._run_cerebro()
        
        
    # CURRENT
    @error_tracking_decorator
    def _run_cerebro(self):
        self.strats = self.cerebro.run()

    def show(self):

        # Plot the results
        figs = self.cerebro.plot(
            iplot=True, 
            # style="pincandle", 
            # width=60 * 10, height=40 * 10,
            figsize=(100, 80),
        )
        
        return figs
    
    def return_analysis(self):
        print('Sharpe Ratio: ', self.strats[0].analyzers.SharpeRatio.get_analysis())
        
        result = {
            'SharpeRatio': self.strats[0].analyzers.SharpeRatio.get_analysis()['sharperatio'],
            'StartingCash': self.cerebro.broker.startingcash,
            'TotalReturn': self.cerebro.broker.getvalue() - self.cerebro.broker.startingcash,
            'FinalPortfolioValue': self.cerebro.broker.getvalue()
        }
        
        return result
        
