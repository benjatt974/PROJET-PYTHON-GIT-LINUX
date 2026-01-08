import pandas as pd
import numpy as np

TRADING_DAYS = 252

def compute_returns(prices: pd.DataFrame) -> pd.DataFrame:
    return prices.pct_change().dropna()

def equal_weights(tickers) -> pd.Series:
    w = np.ones(len(tickers)) / len(tickers)
    return pd.Series(w, index=tickers)

def portfolio_returns(prices: pd.DataFrame, weights: pd.Series) -> pd.Series:
    rets = compute_returns(prices)
    weights = weights.reindex(prices.columns).fillna(0)
    weights = weights / weights.sum()
    port = rets.dot(weights)
    port.name = "portfolio_returns"
    return port

def portfolio_value_from_returns(port_rets: pd.Series, initial: float = 1000.0) -> pd.Series:
    val = initial * (1 + port_rets).cumprod()
    val.name = "portfolio_value"
    return val

def portfolio_value(prices: pd.DataFrame, weights: pd.Series, initial: float = 1000.0) -> pd.Series:
    port_rets = portfolio_returns(prices, weights)
    return portfolio_value_from_returns(port_rets, initial=initial)

def max_drawdown(series: pd.Series) -> float:
    peak = series.cummax()
    dd = (series / peak) - 1.0
    return float(dd.min())

def total_return(series: pd.Series) -> float:
    return float(series.iloc[-1] / series.iloc[0] - 1.0)

def sharpe_ratio(port_rets: pd.Series, rf: float = 0.0) -> float:
    # rf = taux sans risque (0 par défaut)
    excess = port_rets - rf / TRADING_DAYS
    if excess.std() == 0:
        return 0.0
    return float(np.sqrt(TRADING_DAYS) * excess.mean() / excess.std())

def backtest_ma_cross(port_value: pd.Series, short: int, long: int) -> pd.Series:
    """
    Stratégie type Quant A mais appliquée à la valeur du portefeuille :
    - si MA courte > MA longue => investi (1)
    - sinon => cash (0)
    """
    ma_s = port_value.rolling(short).mean()
    ma_l = port_value.rolling(long).mean()
    signal = (ma_s > ma_l).astype(int).fillna(0)

    # Rendements du "prix" (port_value)
    rets = port_value.pct_change().fillna(0)
    strat_rets = rets * signal.shift(1).fillna(0)  # on prend position le lendemain

    strat_val = portfolio_value_from_returns(strat_rets, initial=float(port_value.iloc[0]))
    strat_val.name = "strategy_value"
    return strat_val

def corr_matrix(prices: pd.DataFrame) -> pd.DataFrame:
    return compute_returns(prices).corr()

