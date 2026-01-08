import pandas as pd
import numpy as np

TRADING_DAYS = 252


# -----------------------------
# Basics
# -----------------------------
def compute_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Daily returns from price dataframe."""
    return prices.pct_change().dropna()


def equal_weights(tickers) -> pd.Series:
    w = np.ones(len(tickers)) / len(tickers)
    return pd.Series(w, index=tickers)


def _normalize_weights(weights: pd.Series) -> pd.Series:
    s = float(weights.sum())
    if s == 0:
        # fallback equal weights
        w = np.ones(len(weights)) / len(weights)
        return pd.Series(w, index=weights.index)
    return weights / s


def portfolio_returns(prices: pd.DataFrame, weights: pd.Series) -> pd.Series:
    rets = compute_returns(prices)
    w = weights.reindex(prices.columns).fillna(0)
    w = _normalize_weights(w)
    port = rets.dot(w)
    port.name = "portfolio_returns"
    return port


def portfolio_value_from_returns(port_rets: pd.Series, initial: float = 1000.0) -> pd.Series:
    val = float(initial) * (1 + port_rets).cumprod()
    val.name = "portfolio_value"
    return val


def portfolio_value(prices: pd.DataFrame, weights: pd.Series, initial: float = 1000.0) -> pd.Series:
    port_rets = portfolio_returns(prices, weights)
    return portfolio_value_from_returns(port_rets, initial=initial)


# -----------------------------
# Metrics
# -----------------------------
def max_drawdown(series: pd.Series) -> float:
    peak = series.cummax()
    dd = (series / peak) - 1.0
    return float(dd.min())


def total_return(series: pd.Series) -> float:
    return float(series.iloc[-1] / series.iloc[0] - 1.0)


def sharpe_ratio(port_rets: pd.Series, rf: float = 0.0) -> float:
    """rf annualized (e.g. 0.02)."""
    excess = port_rets - (rf / TRADING_DAYS)
    std = float(excess.std())
    if std == 0 or np.isnan(std):
        return 0.0
    return float(np.sqrt(TRADING_DAYS) * excess.mean() / std)


def annualized_volatility(port_rets: pd.Series) -> float:
    v = float(port_rets.std() * np.sqrt(TRADING_DAYS))
    return 0.0 if np.isnan(v) else v


def corr_matrix(prices: pd.DataFrame) -> pd.DataFrame:
    return compute_returns(prices).corr()


# -----------------------------
# Strategy (MA cross on portfolio value)
# -----------------------------
def backtest_ma_cross(port_value: pd.Series, short: int, long: int) -> pd.Series:
    """
    MA cross applied on portfolio value:
    - invested if short MA > long MA
    - else cash
    """
    if short >= long:
        out = port_value.copy()
        out.name = "strategy_value"
        return out

    ma_s = port_value.rolling(short).mean()
    ma_l = port_value.rolling(long).mean()
    signal = (ma_s > ma_l).astype(int).fillna(0)

    rets = port_value.pct_change().fillna(0)
    strat_rets = rets * signal.shift(1).fillna(0)  # take position next day

    strat_val = portfolio_value_from_returns(strat_rets, initial=float(port_value.iloc[0]))
    strat_val.name = "strategy_value"
    return strat_val


# -----------------------------
# Allocation optimizers
# -----------------------------
def min_variance_weights(prices: pd.DataFrame, long_only: bool = True) -> pd.Series:
    """
    Global minimum variance weights (closed form).
    """
    rets = compute_returns(prices)
    if rets.empty:
        return equal_weights(prices.columns)

    cov = rets.cov().values
    n = cov.shape[0]
    cov = cov + 1e-8 * np.eye(n)  # stabilisation

    ones = np.ones(n)
    inv = np.linalg.pinv(cov)     # more robust than inv
    w = inv @ ones
    w = w / w.sum()

    w = pd.Series(w, index=rets.columns)

    if long_only:
        w = w.clip(lower=0)
        w = _normalize_weights(w)

    return w


def max_sharpe_weights(prices: pd.DataFrame, rf: float = 0.0, long_only: bool = True) -> pd.Series:
    """
    Max Sharpe weights (tangency portfolio, closed form).
    rf annualized.
    """
    rets = compute_returns(prices)
    if rets.empty:
        return equal_weights(prices.columns)

    mu = rets.mean().values * TRADING_DAYS
    cov = rets.cov().values * TRADING_DAYS
    n = cov.shape[0]
    cov = cov + 1e-8 * np.eye(n)

    inv = np.linalg.pinv(cov)
    w = inv @ (mu - rf)

    w = pd.Series(w, index=rets.columns)
    if float(w.abs().sum()) == 0:
        w = equal_weights(rets.columns)

    if long_only:
        w = w.clip(lower=0)

    w = _normalize_weights(w)
    return w


def diversification_ratio(prices: pd.DataFrame, weights: pd.Series) -> float:
    """
    Diversification Ratio = (sum w_i * vol_i) / vol_port
    """
    rets = compute_returns(prices)
    if rets.empty:
        return 0.0

    vol_assets = rets.std() * np.sqrt(TRADING_DAYS)

    w = weights.reindex(rets.columns).fillna(0)
    w = _normalize_weights(w)

    port_vol = float((rets.dot(w)).std() * np.sqrt(TRADING_DAYS))
    if port_vol == 0 or np.isnan(port_vol):
        return 0.0

    return float((w * vol_assets).sum() / port_vol)
