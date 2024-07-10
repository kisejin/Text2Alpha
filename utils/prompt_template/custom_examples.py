import backtrader as bt


class CustomIndicator(bt.Indicator):
    """"""

    lines = ("pvt",)
    params = (("period", 1),)

    def init(self):
        self.addminperiod(self.params.period)

    def next(self):
        if len(self) == 1:
            self.lines.pvt[0] = 0  # Initialize PVT at the beginning
        else:
            prev_close = self.data.close[-1]
            current_close = self.data.close[0]
            volume = self.data.volume[0]
            self.lines.pvt[0] = (
                self.lines.pvt[-1]
                + ((current_close - prev_close) / prev_close) * volume
            )


# Define a specific strategy using the custom PVT indicator
class BackTestStrategy(BaseStrategy):
    def init(self, *args, **kwargs):
        super().init(*args, **kwargs)
        # Initialize the PVT indicator
        self.pvt = PVT()

    def execute(self):
        """
        Define the trading logic based on the PVT indicator.

        Returns:

        int: Trading signal: 1 (long), -1 (sell), or None if no signal."""
        if self.pvt[0] > self.pvt[-1]:  # Example logic: if PVT is increasing
            return 1  # Long signal
        elif self.pvt[0] < self.pvt[-1]:  # Example logic: if PVT is decreasing
            return -1  # Short signal
        return None  # No signal
