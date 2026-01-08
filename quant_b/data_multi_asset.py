import yfinance as yf
import pandas as pd
import datetime as dt

def get_price_history_multi(tickers, start, end=None, interval="1d"):
    """
    Retourne un DataFrame : index=dates, colonnes=tickers, valeurs=Close.
    """
    if end is None:
        end = dt.datetime.today().strftime("%Y-%m-%d")

    data = yf.download(
        tickers,
        start=start,
        end=end,
        interval=interval,
        group_by="column",
        auto_adjust=False,
        progress=False,
    )

    # On prend Close (cohérent avec Quant A)
    prices = data["Close"].copy()

    # Si un seul ticker => Series
    if isinstance(prices, pd.Series):
        prices = prices.to_frame(name=tickers[0])

    prices = prices.dropna(how="all")
    prices = prices.dropna(how="any")  # dates communes à tous
    return prices
