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

    # --- Inputs
    tickers = st.multiselect(
        "Choisis au moins 3 actifs",
        ["SPY", "TLT", "GLD", "AAPL", "MSFT", "AMZN", "BTC-USD", "ETH-USD"],
        default=["SPY", "TLT", "GLD"],
    )

    if len(tickers) < 3:
        st.warning("Il faut sélectionner au moins 3 actifs.")
        return

    col1, col2 = st.columns(2)
    with col1:
        start = st.date_input("Date de début", value=pd.to_datetime("2021-01-01"))
    with col2:
        end = st.date_input("Date de fin", value=pd.to_datetime("today"))

    st.subheader("Paramètres du portefeuille")
    initial_capital = st.number_input("Capital initial", value=1000.0, step=100.0)

    # Poids
    mode = st.selectbox("Allocation", ["Equal Weight", "Custom Weights"])
    if mode == "Equal Weight":
        weights = equal_weights(tickers)
    else:
        st.caption("Ajuste les poids (ils seront normalisés automatiquement).")
        w_dict = {}
        cols = st.columns(min(4, len(tickers)))
        for i, t in enumerate(tickers):
            with cols[i % len(cols)]:
                w_dict[t] = st.slider(f"{t}", 0.0, 1.0, 1.0/len(tickers), 0.01)
        weights = pd.Series(w_dict)

    # Stratégie
    st.subheader("Stratégie (comme Quant A, appliquée au portefeuille)")
    use_ma = st.checkbox("Activer MA Cross sur le portefeuille", value=True)
    short = st.slider("MA courte", 5, 100, 20)
    long = st.slider("MA longue", 10, 300, 50)

    # --- Button
    if st.button("Lancer le backtest"):
        prices = get_price_history_multi(tickers, str(start), str(end))

        st.subheader("Prix (Close) — actifs")
        st.line_chart(prices)

        # Portefeuille buy&hold
        port_val = portfolio_value(prices, weights, initial=initial_capital)
        port_rets = portfolio_returns(prices, weights)

        # Stratégie
        if use_ma and short < long:
            strat_val = backtest_ma_cross(port_val, short=short, long=long)
        else:
            strat_val = port_val.copy()
            strat_val.name = "strategy_value"

        # Metrics
        c1, c2, c3 = st.columns(3)
        c1.metric("Sharpe (portefeuille)", f"{sharpe_ratio(port_rets):.2f}")
        c2.metric("Max Drawdown (portefeuille)", f"{max_drawdown(port_val)*100:.1f}%")
        c3.metric("Performance totale (portefeuille)", f"{total_return(port_val)*100:.1f}%")

        st.subheader("Valeur du portefeuille vs valeur de la stratégie")
        df_plot = pd.DataFrame({
            "Portefeuille (Buy&Hold)": port_val,
            "Stratégie": strat_val
        })
        st.line_chart(df_plot)

        st.subheader("Corrélation (rendements)")
        st.dataframe(corr_matrix(prices))

        # Comparaison base 100 (optionnel mais très utile)
        st.subheader("Comparaison normalisée (base 100)")
        base100_assets = (prices / prices.iloc[0]) * 100
        base100_port = (port_val / port_val.iloc[0]) * 100
        comp = base100_assets.copy()
        comp["Portfolio"] = base100_port
        st.line_chart(comp)
    else:
        st.info("Choisis tes paramètres puis clique sur **Lancer le backtest**.")
