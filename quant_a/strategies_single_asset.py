import pandas as pd

def _to_series(x: pd.Series | pd.DataFrame) -> pd.Series:
    """Assure qu'on travaille toujours avec une Series."""
    if isinstance(x, pd.DataFrame):
        return x.iloc[:, 0]
    return x

def buy_and_hold(prices: pd.Series, initial_capital: float = 1000.0) -> pd.Series:
    """
    Stratégie Buy & Hold : on achète au début et on ne touche plus.
    Retourne la courbe de valeur du portefeuille.
    """
    prices = _to_series(prices)
    returns = prices.pct_change().fillna(0)
    cumulative = (1 + returns).cumprod()
    return initial_capital * cumulative

def ma_crossover(
    prices: pd.Series,
    short_window: int = 20,
    long_window: int = 50,
    initial_capital: float = 1000.0,
) -> pd.Series:
    """
    Stratégie momentum : croisement de moyennes mobiles.
    Investi (1) si MA courte > MA longue, cash (0) sinon.
    """
    prices = _to_series(prices)

    ma_short = prices.rolling(window=short_window).mean()
    ma_long = prices.rolling(window=long_window).mean()

    signal = (ma_short > ma_long).astype(int)
    daily_returns = prices.pct_change().fillna(0)

    strategy_returns = signal.shift(1).fillna(0) * daily_returns
    cumulative = (1 + strategy_returns).cumprod()
    return initial_capital * cumulative
