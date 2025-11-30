import pandas as pd
import numpy as np

def compute_daily_returns(values: pd.Series) -> pd.Series:
    """Rendements simples journaliers (ou par période choisie)."""
    return values.pct_change().fillna(0)

def sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
    """
    Sharpe annualisé (~252 jours de trading).
    """
    excess = returns - risk_free_rate / 252
    mean_excess = excess.mean()
    std_excess = excess.std()
    if std_excess == 0:
        return np.nan
    return (mean_excess / std_excess) * np.sqrt(252)

def max_drawdown(values: pd.Series) -> float:
    """
    Max drawdown (plus forte perte relative).
    """
    running_max = values.cummax()
    drawdowns = values / running_max - 1.0
    return drawdowns.min()

def total_return(values: pd.Series) -> float:
    """
    Perf totale entre le début et la fin.
    """
    if len(values) < 2:
        return 0.0
    return values.iloc[-1] / values.iloc[0] - 1.0
