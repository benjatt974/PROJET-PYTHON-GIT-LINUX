import streamlit as st
import pandas as pd
import numpy as np

from quant_b.data_multi_asset import get_price_history_multi
from quant_b.portfolio import (
    equal_weights, portfolio_returns, portfolio_value,
    sharpe_ratio, max_drawdown, total_return,
    backtest_ma_cross, corr_matrix,
    annualized_volatility, diversification_ratio,
    min_variance_weights, max_sharpe_weights
)

# ---- Petit style dark + cartes
DARK_CSS = """
<style>
.block-container {padding-top: 1.2rem;}
.card {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 14px;
  padding: 16px 16px;
}
.small {opacity:0.8; font-size: 0.9rem;}
.tickerbar{
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 14px;
  padding: 10px 14px;
  overflow-x:auto;
  white-space: nowrap;
}
.titem{display:inline-block; margin-right:16px; font-weight:600;}
.pos{color:#30d158;}
.neg{color:#ff453a;}
</style>
"""

def _ticker_bar(prices: pd.DataFrame):
    # dernier close + variation 1j
    if prices.shape[0] < 2:
        return
    last = prices.iloc[-1]
    prev = prices.iloc[-2]
    chg = (last / prev - 1.0) * 100

    html = '<div class="tickerbar">'
    for t in prices.columns:
        c = chg[t]
        cls = "pos" if c >= 0 else "neg"
        html += f'<span class="titem">{t}  ${last[t]:.2f}  <span class="{cls}">{c:+.2f}%</span></span>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

def run_quant_b_page():
    st.markdown(DARK_CSS, unsafe_allow_html=True)

    # Layout type "panel gauche + dashboard droite"
    left, right = st.columns([1.05, 2.95], gap="large")

    with left:
        st.markdown("## Portfolio Controls")

        tickers = st.multiselect(
            "Selected Assets (min 3)",
            ["SPY", "QQQ", "TLT", "GLD", "AAPL", "MSFT", "AMZN", "GOOGL", "META", "NVDA", "BTC-USD", "ETH-USD"],
            default=["AAPL", "MSFT", "GOOGL", "BTC-USD", "META"],
        )

        if len(tickers) < 3:
            st.warning("Sélectionne au moins 3 actifs.")
            return

        col1, col2 = st.columns(2)
        with col1:
            start = st.date_input("Start", value=pd.to_datetime("2021-01-01"))
        with col2:
            end = st.date_input("End", value=pd.to_datetime("today"))

        st.markdown("### Weighting Strategy")
        strategy = st.selectbox(
            "Allocation",
            ["Equal Weights", "Minimum Variance", "Max Sharpe Ratio", "Custom Weights"],
            index=2
        )
        long_only = st.checkbox("Long-only (pas de poids négatifs)", value=True)

        initial_capital = st.number_input("Capital initial", value=1000.0, step=100.0)

        st.markdown("### Strategy (MA Cross on portfolio)")
        use_ma = st.checkbox("Enable MA Cross", value=True)
        short = st.slider("MA short", 5, 100, 20)
        long = st.slider("MA long", 10, 300, 50)

        run = st.button("▶ Run Backtest", use_container_width=True)

    with right:
        st.markdown("# Portfolio Analysis")
        st.markdown('<div class="small">Multi-assets • Allocation • MA Cross option</div>', unsafe_allow_html=True)

        if not run:
            st.info("Configure à gauche puis clique sur **Run Backtest**.")
            return

        prices = get_price_history_multi(tickers, str(start), str(end)).dropna()

        _ticker_bar(prices)

        # --- Weights
        if strategy == "Equal Weights":
            weights = equal_weights(prices.columns)
        elif strategy == "Minimum Variance":
            weights = min_variance_weights(prices, long_only=long_only)
        elif strategy == "Max Sharpe Ratio":
            weights = max_sharpe_weights(prices, rf=0.0, long_only=long_only)
        else:
            st.markdown("**Custom Weights** (ajuste puis normalisation)")
            w = {}
            for t in prices.columns:
                w[t] = st.slider(f"{t}", 0.0, 1.0, 1.0/len(prices.columns), 0.01)
            weights = pd.Series(w)
            weights = weights / weights.sum()

        # --- Portfolio series
        port_val = portfolio_value(prices, weights, initial=initial_capital)
        port_rets = portfolio_returns(prices, weights)

        # --- Strategy on portfolio value
        if use_ma and short < long:
            strat_val = backtest_ma_cross(port_val, short=short, long=long)
        else:
            strat_val = port_val.copy()
            strat_val.name = "strategy_value"

        # --- Metrics cards
        m1, m2, m3, m4 = st.columns(4)
        port_ret = total_return(port_val) * 100
        vol = annualized_volatility(port_rets) * 100
        sr = sharpe_ratio(port_rets)
        dr = diversification_ratio(prices, weights)

        m1.markdown(f'<div class="card"><div class="small">Portfolio Return</div><div style="font-size:28px;font-weight:800">{port_ret:+.2f}%</div></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="card"><div class="small">Portfolio Volatility</div><div style="font-size:28px;font-weight:800">{vol:.2f}%</div></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="card"><div class="small">Sharpe Ratio</div><div style="font-size:28px;font-weight:800">{sr:.2f}</div></div>', unsafe_allow_html=True)
        m4.markdown(f'<div class="card"><div class="small">Diversification Ratio</div><div style="font-size:28px;font-weight:800">{dr:.2f}</div></div>', unsafe_allow_html=True)

        st.markdown("### Portfolio Performance")

        # Base 100 comparatif (assets + portfolio + strategy)
        base100_assets = (prices / prices.iloc[0]) * 100
        base100_port = (port_val / port_val.iloc[0]) * 100
        base100_strat = (strat_val / strat_val.iloc[0]) * 100

        perf = base100_assets.copy()
        perf["Portfolio"] = base100_port
        perf["Strategy"] = base100_strat
        st.line_chart(perf)

        # Weights table
        st.markdown("### Weights")
        wdf = weights.sort_values(ascending=False).to_frame("weight")
        st.dataframe((wdf * 100).round(2).rename(columns={"weight":"%"}), use_container_width=True)

        st.markdown("### Asset Correlation Matrix")
        st.dataframe(corr_matrix(prices), use_container_width=True)

        st.markdown("### Drawdown")
        dd = (port_val / port_val.cummax() - 1.0) * 100
        st.line_chart(dd.to_frame("Drawdown (%)"))

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

