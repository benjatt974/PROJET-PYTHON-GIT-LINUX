import streamlit as st
import pandas as pd
import datetime as dt

from quant_a.data_single_asset import get_price_history
from quant_a.strategies_single_asset import buy_and_hold, ma_crossover
from quant_a.metrics_single_asset import (
    compute_daily_returns,
    sharpe_ratio,
    max_drawdown,
    total_return,
)


def run_quant_a_page():
    st.title("Quant A – Single Asset")
    st.markdown("Analyse et backtesting d’un actif financier unique.")
    st.markdown("---")

    # ===== Sidebar : paramètres =====
    st.sidebar.subheader("Paramètres de marché")

    ticker = st.sidebar.text_input("Ticker", value="BTC-USD")

    col_start, col_end = st.sidebar.columns(2)
    with col_start:
        start_date = st.date_input("Début", value=dt.date(2020, 1, 1))
    with col_end:
        end_date = st.date_input("Fin", value=dt.date.today())

    interval = st.sidebar.selectbox(
        "Périodicité",
        ["1d", "1h"],
        index=0,
    )

    st.sidebar.subheader("Paramètres de stratégie")

    strategy_name = st.sidebar.selectbox(
        "Stratégie",
        ["Buy & Hold", "MA Crossover"],
    )

    initial_capital = st.sidebar.number_input(
        "Capital initial",
        min_value=100.0,
        value=1000.0,
        step=100.0,
    )

    short_window = st.sidebar.slider("MA courte", 5, 50, 20)
    long_window = st.sidebar.slider("MA longue", 20, 200, 50)

    run_backtest = st.sidebar.button("Lancer le backtest")

    if not run_backtest:
        st.info("Configure les paramètres à gauche puis clique sur **Lancer le backtest**.")
        return

    # ===== Récupération des données =====
    data = get_price_history(
        ticker=ticker,
        start=str(start_date),
        end=str(end_date),
        interval=interval,
    )

    if data.empty:
        st.error("Aucune donnée trouvée pour ce ticker / cette période.")
        return

    prices = data["price"]

    # ===== Choix de la stratégie =====
    if strategy_name == "Buy & Hold":
        strategy_values = buy_and_hold(prices, initial_capital)
    else:
        strategy_values = ma_crossover(
            prices,
            short_window=short_window,
            long_window=long_window,
            initial_capital=initial_capital,
        )

    # ===== Métriques =====
    returns = compute_daily_returns(strategy_values)
    sr = sharpe_ratio(returns)
    mdd = max_drawdown(strategy_values)
    perf = total_return(strategy_values)

    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Sharpe ratio", f"{sr:.2f}" if pd.notna(sr) else "N/A")
    kpi2.metric("Max drawdown", f"{mdd:.1%}")
    kpi3.metric("Performance totale", f"{perf:.1%}")

    st.markdown("")

    # ===== Graph principal =====
    st.subheader("Prix vs valeur de la stratégie")

    df_plot = pd.concat([prices, strategy_values], axis=1)
    df_plot.columns = ["Asset Price", f"Strategy – {strategy_name}"]

    st.line_chart(df_plot)

    # ===== Détails optionnels =====
    with st.expander("Données récentes"):
        st.dataframe(df_plot.tail(15))
