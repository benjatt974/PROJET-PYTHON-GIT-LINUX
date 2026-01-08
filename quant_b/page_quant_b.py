import streamlit as st
import pandas as pd

from quant_b.data_multi_asset import get_price_history_multi
from quant_b.portfolio import equal_weights, portfolio_value, corr_matrix

def run_quant_b_page():
    st.title("Quant B — Portefeuille Multi-Actifs")

    tickers = st.multiselect(
        "Choisis au moins 3 actifs",
        ["SPY", "TLT", "GLD", "AAPL", "MSFT", "AMZN", "BTC-USD", "ETH-USD"],
        default=["SPY", "TLT", "GLD"],
    )

    if len(tickers) < 3:
        st.warning("Il faut sélectionner au moins 3 actifs.")
        return

    start = st.date_input("Date de début", value=pd.to_datetime("2021-01-01"))
    end = st.date_input("Date de fin", value=pd.to_datetime("today"))

    prices = get_price_history_multi(tickers, str(start), str(end))

    st.subheader("Prix (Close)")
    st.line_chart(prices)

    # Portefeuille equal weight
    w = equal_weights(tickers)
    port_val = portfolio_value(prices, w, initial=100.0)

    st.subheader("Valeur cumulée du portefeuille (Equal Weight)")
    st.line_chart(port_val)

    st.subheader("Matrice de corrélation (rendements)")
    st.dataframe(corr_matrix(prices))
