import backtrader as bt
# Define a specific strategy inheriting from `BaseStrategy` using a simple moving average indicator.
class BackTestStrategy(BaseStrategy):
    """
    Simple BackTestStrategy using Moving Average Indicator.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sma = bt.ind.SMA(self.data.close, period=15)

    def execute(self):
        """
        Define the trading logic based on the moving average crossover.

        Returns:
        - int: Trading signal: 1 (long), -1 (sell), or None if no signal.
        """
        if self.sma > self.data.close:
            return 1  # Long signal
        elif self.sma < self.data.close:
            return -1  # Short signal
        return None  # No signal