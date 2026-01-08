import streamlit as st
import pandas as pd

from quant_b.data_multi_asset import get_price_history_multi
from quant_b.portfolio import (
    equal_weights, portfolio_returns, portfolio_value,
    sharpe_ratio, max_drawdown, total_return,
    backtest_ma_cross, corr_matrix
)

def run_quant_b_page():
    st.title("Quant B — Portefeuille Multi-Actifs")
    st.caption("Backtesting multi-actifs + stratégie MA Cross appliquée au portefeuille.")

    # -------------------------
    # SIDEBAR (comme Quant A)
    # -------------------------
    st.sidebar.header("Paramètres du portefeuille")

    tickers = st.sidebar.multiselect(
        "Tickers (au moins 3)",
        ["SPY", "TLT", "GLD", "AAPL", "MSFT", "AMZN", "BTC-USD", "ETH-USD"],
        default=["SPY", "TLT", "GLD"],
    )

    colD1, colD2 = st.sidebar.columns(2)
    with colD1:
        start = st.date_input("Début", value=pd.to_datetime("2021-01-01"))
    with colD2:
        end = st.date_input("Fin", value=pd.to_datetime("today"))

    initial_capital = st.sidebar.number_input("Capital initial", value=1000.0, step=100.0)

    st.sidebar.subheader("Allocation")
    mode = st.sidebar.selectbox("Méthode", ["Equal Weight", "Custom Weights"])

    if len(tickers) > 0:
        if mode == "Equal Weight":
            weights = equal_weights(tickers)
        else:
            st.sidebar.caption("Ajuste les poids (normalisés automatiquement).")
            w_dict = {}
            for t in tickers:
                w_dict[t] = st.sidebar.slider(t, 0.0, 1.0, 1.0 / max(len(tickers), 1), 0.01)
            weights = pd.Series(w_dict)
    else:
        weights = pd.Series(dtype=float)

    st.sidebar.subheader("Stratégie")
    use_ma = st.sidebar.checkbox("Activer MA Cross", value=True)
    short = st.sidebar.slider("MA courte", 5, 100, 20)
    long = st.sidebar.slider("MA longue", 10, 300, 50)

    run = st.sidebar.button("Lancer le backtest")

    # -------------------------
    # VALIDATION
    # -------------------------
    if len(tickers) < 3:
        st.warning("Il faut sélectionner au moins 3 actifs.")
        st.stop()

    if use_ma and short >= long:
        st.warning("La MA courte doit être strictement inférieure à la MA longue.")
        st.stop()

    if not run:
        st.info("Configure les paramètres à gauche puis clique sur **Lancer le backtest**.")
        st.stop()

    # -------------------------
    # BACKTEST
    # -------------------------
    prices = get_price_history_multi(tickers, str(start), str(end))

    st.subheader("Prix (Close) — actifs")
    st.line_chart(prices)

    # Portefeuille buy&hold
    port_val = portfolio_value(prices, weights, initial=initial_capital)
    port_rets = portfolio_returns(prices, weights)

    # Stratégie
    if use_ma:
        strat_val = backtest_ma_cross(port_val, short=short, long=long)
    else:
        strat_val = port_val.copy()
        strat_val.name = "strategy_value"

    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Sharpe (portefeuille)", f"{sharpe_ratio(port_rets):.2f}")
    c2.metric("Max Drawdown (portefeuille)", f"{max_drawdown(port_val)*100:.1f}%")
    c3.metric("Performance totale (portefeuille)", f"{total_return(port_val)*100:.1f}%")

    st.subheader("Valeur du portefeuille vs stratégie")
    df_plot = pd.DataFrame({
        "Portefeuille (Buy&Hold)": port_val,
        "Stratégie": strat_val
    })
    st.line_chart(df_plot)

    st.subheader("Corrélation (rendements)")
    st.dataframe(corr_matrix(prices))

    st.subheader("Comparaison normalisée (base 100)")
    base100_assets = (prices / prices.iloc[0]) * 100
    base100_port = (port_val / port_val.iloc[0]) * 100
    comp = base100_assets.copy()
    comp["Portfolio"] = base100_port
    st.line_chart(comp)

