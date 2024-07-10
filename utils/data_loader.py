import yfinance as yf
import pandas as pd
import importlib
from typing import Optional
# from .VietNamStockPrice.utils import get_logger
# from .VietNamStockPrice.msn.const import _CURRENCY_ID_MAP, _GLOBAL_INDICES, _CRYPTO_ID_MAP


# logger = get_logger(__name__)

# class Quote:
#     """
#     Class manage standardized data sources for candlestick data, the returned data depends on the chosen available data source.
#     """
#     SUPPORTED_SOURCES = ["VCI", "TCBS", "MSN"]

#     def __init__(self, symbol: str, source: str = "VCI"):

#         self.source = source.upper()
#         if self.source not in self.SUPPORTED_SOURCES:
#             raise ValueError(f"Currently, there is only supported data from {', '.join(self.SUPPORTED_SOURCES)}.")
#         self.symbol = symbol.upper()
#         self.source_module = f"ver_3.VietNamStockPrice.{source.lower()}"
#         self.data_source = self._load_data_source()

#     def _load_data_source(self):
#         """
#         Direct the chosen data source class.
#         """
#         module = importlib.import_module(self.source_module)
#         if self.source == "MSN":
#             return module.Quote(self.symbol.lower())
#         else:
#             return module.Quote(self.symbol)
    
#     def _update_data_source(self, symbol: Optional[str] = None):
#         """
#         Update the data source if a new symbol is provided.
#         """
#         if self.source != 'MSN':
#             if symbol:
#                 self.symbol = symbol.upper()
#                 self.data_source = self._load_data_source()
#         else:
#             self.data_source = self._load_data_source()
        
#     def history(self, symbol: Optional[str] = None, **kwargs):
#         """
#         Extract historical price data from the chosen data source.
#         """
#         if self.source == "MSN":
#             symbol_map = {**_CURRENCY_ID_MAP, **_GLOBAL_INDICES, **_CRYPTO_ID_MAP}
#             if symbol:
#                 self.symbol = symbol_map[symbol]
#                 logger.info(f"Convert the {symbol} stock to MSN stock code: {self.symbol}")
#                 self._update_data_source(symbol=self.symbol)
#                 return self.data_source.history(**kwargs)
#         else:
#             if symbol:
#                 self.symbol = symbol.upper()
#             self._update_data_source(self.symbol)
#             return self.data_source.history(**kwargs)
        
#         self._update_data_source(self.symbol)
#         return self.data_source.history(**kwargs)
    
#     def intraday(self, symbol: Optional[str] = None, **kwargs):
#         """
#         Extract intraday trading data from the chosen data source.
#         """
#         # if symbol is provided, override the symbol
#         self._update_data_source(symbol)
#         return self.data_source.intraday(**kwargs)
    
#     def price_depth(self, symbol: Optional[str] = None, **kwargs):
#         """
#         Extract volume data by price step from the chosen data source.
#         """
#         self._update_data_source(symbol)
#         return self.data_source.price_depth(**kwargs)

def load_stock_data(ticker, period="1y"):
    data = yf.download(ticker, period=period)
    data["Date"] = data.index
    data["Date"] = data["Date"].apply(lambda dt: dt.replace(tzinfo=None))
    data = data.resample("5min", on="Date", label="right").agg({
        "Open": "first",
        "High": "max",
        "Low": "min",
        "Close": "last",
        "Volume": "sum",
    }).reset_index().dropna()
    return data
