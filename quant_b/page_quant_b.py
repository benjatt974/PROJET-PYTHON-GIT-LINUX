import streamlit as st
import pandas as pd

from quant_b.data_multi_asset import get_price_history_multi
from quant_b.portfolio import (
    equal_weights, portfolio_returns, portfolio_value,
    sharpe_ratio, max_drawdown, total_return,
    backtest_ma_cross, corr_matrix
)

def run_quant_b_page():
    st.title("Portfolio Analysis")

    # --------- Defaults (session state) ----------
    if "qb_params" not in st.session_state:
        st.session_state.qb_params = {
            "tickers": ["AAPL", "MSFT", "GOOGL", "BTC-USD", "META"],
            "start": pd.to_datetime("2021-01-01").date(),
            "end": pd.to_datetime("today").date(),
            "initial": 1000.0,
            "alloc_mode": "Equal Weight",
            "use_ma": True,
            "short": 20,
            "long": 50,
        }
    p = st.session_state.qb_params

    # --------- BIG RESULTS AREA (top) ----------
    results = st.container()

    # Affiche les résultats si on a déjà lancé au moins 1 fois
    if st.session_state.get("qb_run", False):
        tickers = p["tickers"]
        prices = get_price_history_multi(tickers, str(p["start"]), str(p["end"]))

        # Portefeuille buy&hold
        weights = equal_weights(tickers)
        port_val = portfolio_value(prices, weights, initial=p["initial"])
        port_rets = portfolio_returns(prices, weights)

        # Stratégie MA cross sur portefeuille
        if p["use_ma"] and p["short"] < p["long"]:
            strat_val = backtest_ma_cross(port_val, short=p["short"], long=p["long"])
        else:
            strat_val = port_val.copy()
            strat_val.name = "strategy_value"

        with results:
            # Bandeau “ticker strip” (simple)
            st.caption("Multi-assets • Allocation • MA Cross option")

            # Metrics cards
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Portfolio Return", f"{total_return(port_val)*100:.2f}%")
            c2.metric("Portfolio Volatility", f"{(port_rets.std()*(252**0.5))*100:.2f}%")
            c3.metric("Sharpe Ratio", f"{sharpe_ratio(port_rets):.2f}")
            # “Diversification ratio” simplifié (optionnel)
            c4.metric("Diversification", f"{(1.0 - corr_matrix(prices).values.mean()):.2f}")

            st.subheader("Portfolio Performance")
            base100_assets = (prices / prices.iloc[0]) * 100
            base100_port = (port_val / port_val.iloc[0]) * 100
            base100_strat = (strat_val / strat_val.iloc[0]) * 100
            perf = base100_assets.copy()
            perf["Portfolio"] = base100_port
            perf["Strategy"] = base100_strat
            st.line_chart(perf)

            st.subheader("Asset Correlation Matrix")
            st.dataframe(corr_matrix(prices))

    # --------- CONTROLS (bottom) ----------
    st.markdown("---")
    st.subheader("Portfolio Controls")

    with st.form("qb_controls", border=False):
        tickers = st.multiselect(
            "Selected Assets (min 3)",
            ["SPY", "TLT", "GLD", "AAPL", "MSFT", "AMZN", "GOOGL", "META", "BTC-USD", "ETH-USD"],
            default=p["tickers"],
        )

        col1, col2 = st.columns(2)
        with col1:
            start = st.date_input("Start", value=p["start"])
        with col2:
            end = st.date_input("End", value=p["end"])

        st.subheader("Weighting Strategy")
        alloc_mode = st.selectbox("Allocation", ["Equal Weight", "Custom Weights"], index=0 if p["alloc_mode"] == "Equal Weight" else 1)

        st.checkbox("Long-only (pas de poids négatifs)", value=True, disabled=True)
        initial = st.number_input("Capital initial", value=float(p["initial"]), step=100.0)

        st.subheader("Strategy (MA Cross on portfolio)")
        use_ma = st.checkbox("Enable MA Cross", value=bool(p["use_ma"]))
        short = st.slider("MA short", 5, 100, int(p["short"]))
        long = st.slider("MA long", 10, 300, int(p["long"]))

        submitted = st.form_submit_button("Lancer le backtest")

    if submitted:
        if len(tickers) < 3:
            st.warning("Il faut sélectionner au moins 3 actifs.")
        else:
            st.session_state.qb_params.update({
                "tickers": tickers,
                "start": start,
                "end": end,
                "initial": initial,
                "alloc_mode": alloc_mode,
                "use_ma": use_ma,
                "short": short,
                "long": long,
            })
            st.session_state.qb_run = True
            st.rerun()

