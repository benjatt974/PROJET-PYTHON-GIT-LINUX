import pandas as pd
import numpy as np

def compute_returns(prices: pd.DataFrame) -> pd.DataFrame:
    return prices.pct_change().dropna()

def equal_weights(tickers) -> pd.Series:
    w = np.ones(len(tickers)) / len(tickers)
    return pd.Series(w, index=tickers)

def portfolio_value(prices: pd.DataFrame, weights: pd.Series, initial=100.0) -> pd.Series:
    rets = compute_returns(prices)
    weights = weights.reindex(prices.columns).fillna(0)
    port_rets = rets.dot(weights)
    value = initial * (1 + port_rets).cumprod()
    value.name = "Portfolio"
    return value

def corr_matrix(prices: pd.DataFrame) -> pd.DataFrame:
    return compute_returns(prices).corr()
