import yfinance as yf
import pandas as pd
import datetime as dt

def get_price_history(
    ticker: str,
    start: str,
    end: str | None,
    interval: str = "1d",
) -> pd.DataFrame:
    """
    Récupère l'historique de prix pour un ticker Yahoo Finance.
    Retourne un DataFrame avec une colonne 'price'.
    """
    if end is None:
        end = dt.datetime.today().strftime("%Y-%m-%d")

    data = yf.download(ticker, start=start, end=end, interval=interval)
    data = data[["Close"]].rename(columns={"Close": "price"})
    data.dropna(inplace=True)
    return data
