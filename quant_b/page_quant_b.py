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

# -----------------------------
# STYLE
# -----------------------------
DARK_CSS = """
<style>
.block-container {padding-top: 1.0rem; padding-bottom: 2rem;}
h1,h2,h3 {letter-spacing: -0.02em;}
.small {opacity:0.78; font-size: 0.9rem;}
hr {border-color: rgba(255,255,255,0.08);}

.card {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 16px;
  padding: 14px 16px;
  height: 100%;
}

.tickerbar{
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 16px;
  padding: 10px 14px;
  overflow-x:auto;
  white-space: nowrap;
}

.titem{display:inline-block; margin-right:16px; font-weight:650;}
.pos{color:#30d158;}
.neg{color:#ff453a;}

.section {
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 18px;
  padding: 14px 16px;
}
</style>
"""

# -----------------------------
# UI HELPERS
# -----------------------------
def _ticker_bar(prices: pd.DataFrame):
    """Dernier close + variation 1j"""
    if prices is None or prices.empty or prices.shape[0] < 2:
        return

    last = prices.iloc[-1]
    prev = prices.iloc[-2]
    chg = (last / prev - 1.0) * 100

    html = '<div class="tickerbar">'
    for t in prices.columns:
        c = float(chg[t])
        cls = "pos" if c >= 0 else "neg"
        html += f'<span class="titem">{t}  ${float(last[t]):.2f}  <span class="{cls}">{c:+.2f}%</span></span>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def _metric_card(col, title: str, value: str):
    col.markdown(
        f"""
        <div class="card">
          <div class="small">{title}</div>
          <div style="font-size:28px;font-weight:850;margin-top:2px;">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def _safe_date(d):
    # Streamlit date_input renvoie date/datetime selon les versions
    return pd.to_datetime(d).date()


# -----------------------------
# MAIN PAGE
# -----------------------------
def run_quant_b_page():
    st.markdown(DARK_CSS, unsafe_allow_html=True)

    # ---------- HEADER ----------
    st.markdown("# Portfolio Analysis")
    st.markdown('<div class="small">Multi-assets • Allocation • MA Cross option</div>', unsafe_allow_html=True)

    # ---------- DEFAULT STATE ----------
    if "qb_run" not in st.session_state:
        st.session_state.qb_run = False

    # ---------- CONTROLS (BOTTOM) ----------
    st.markdown("---")

    with st.expander("Portfolio Controls", expanded=True):
        c1, c2, c3 = st.columns([2.2, 1.2, 1.2])

        with c1:
            tickers = st.multiselect(
                "Selected Assets (min 3)",
                ["SPY", "QQQ", "TLT", "GLD", "AAPL", "MSFT", "AMZN", "GOOGL", "META", "NVDA", "BTC-USD", "ETH-USD"],
                default=["AAPL", "MSFT", "GOOGL", "BTC-USD", "META"],
            )

        with c2:
            start = st.date_input("Start", value=pd.to_datetime("2021-01-01"))
            end = st.date_input("End", value=pd.to_datetime("today"))

        with c3:
            initial_capital = st.number_input("Capital initial", value=1000.0, step=100.0)

        if len(tickers) < 3:
            st.warning("Sélectionne au moins 3 actifs.")
            st.session_state.qb_run = False
            return

        st.markdown("#### Allocation")
        a1, a2 = st.columns([1.4, 1.0])
        with a1:
            strategy = st.selectbox(
                "Method",
                ["Equal Weights", "Minimum Variance", "Max Sharpe Ratio", "Custom Weights"],
                index=2
            )
        with a2:
            long_only = st.checkbox("Long-only", value=True)

        # Custom weights sliders (only if needed)
        custom_weights = None
        if strategy == "Custom Weights":
            st.caption("Ajuste les poids (normalisés automatiquement).")
            cols = st.columns(min(4, len(tickers)))
            w = {}
            for i, t in enumerate(tickers):
                with cols[i % len(cols)]:
                    w[t] = st.slider(t, 0.0, 1.0, 1.0/len(tickers), 0.01)
            custom_weights = pd.Series(w)

        st.markdown("#### Strategy (MA Cross on Portfolio)")
        s1, s2, s3 = st.columns([1.0, 1.0, 1.0])
        with s1:
            use_ma = st.checkbox("Enable MA Cross", value=True)
        with s2:
            short = st.slider("MA short", 5, 100, 20)
        with s3:
            long = st.slider("MA long", 10, 300, 50)

        run = st.button("▶ Run Backtest", use_container_width=True)
        if run:
            st.session_state.qb_run = True

    # ---------- STOP IF NOT RUN ----------
    if not st.session_state.qb_run:
        st.info("Configure les contrôles (en bas) puis clique sur **Run Backtest**.")
        return

    # ---------- DATA LOAD ----------
    start_s = str(_safe_date(start))
    end_s = str(_safe_date(end))

    prices = get_price_history_multi(tickers, start_s, end_s)
    if prices is None or prices.empty:
        st.error("Aucune donnée récupérée. Vérifie les tickers / dates.")
        return

    prices = prices.dropna()
    if prices.shape[0] < 30:
        st.warning("Peu de données sur la période : les métriques seront peu fiables.")

    # ---------- WEIGHTS ----------
    if strategy == "Equal Weights":
        weights = equal_weights(prices.columns)

    elif strategy == "Minimum Variance":
        weights = min_variance_weights(prices, long_only=long_only)

    elif strategy == "Max Sharpe Ratio":
        weights = max_sharpe_weights(prices, rf=0.0, long_only=long_only)

    else:
        w = custom_weights.reindex(prices.columns).fillna(0)
        if float(w.sum()) == 0:
            w = equal_weights(prices.columns)
        else:
            w = w / w.sum()
        weights = w

    # ---------- PORTFOLIO ----------
    port_val = portfolio_value(prices, weights, initial=initial_capital)
    port_rets = portfolio_returns(prices, weights)

    # ---------- STRATEGY ON PORTFOLIO ----------
    if use_ma and short < long:
        strat_val = backtest_ma_cross(port_val, short=short, long=long)
    else:
        strat_val = port_val.copy()
        strat_val.name = "strategy_value"

    # ---------- TOP BAR ----------
    _ticker_bar(prices)
    st.markdown("")

    # ---------- METRICS ----------
    m1, m2, m3, m4, m5 = st.columns(5)

    port_ret = total_return(port_val) * 100
    vol = annualized_volatility(port_rets) * 100
    sr = sharpe_ratio(port_rets)
    dd = max_drawdown(port_val) * 100
    dr = diversification_ratio(prices, weights)

    _metric_card(m1, "Portfolio Return", f"{port_ret:+.2f}%")
    _metric_card(m2, "Volatility (ann.)", f"{vol:.2f}%")
    _metric_card(m3, "Sharpe Ratio", f"{sr:.2f}")
    _metric_card(m4, "Max Drawdown", f"{dd:.2f}%")
    _metric_card(m5, "Diversification", f"{dr:.2f}")

    st.markdown("")

    # ---------- PERFORMANCE CHART ----------
    st.markdown("## Portfolio Performance")

    base100_assets = (prices / prices.iloc[0]) * 100
    base100_port = (port_val / port_val.iloc[0]) * 100
    base100_strat = (strat_val / strat_val.iloc[0]) * 100

    perf = base100_assets.copy()
    perf["Portfolio"] = base100_port
    perf["Strategy"] = base100_strat
    st.line_chart(perf, use_container_width=True)

    # ---------- WEIGHTS + TABLES ----------
    st.markdown("## Weights & Diagnostics")
    cA, cB = st.columns([1.2, 1.8], gap="large")

    with cA:
        st.markdown("### Weights")
        wdf = weights.sort_values(ascending=False).to_frame("weight")
        st.dataframe((wdf * 100).round(2).rename(columns={"weight": "%"}), use_container_width=True)

        st.markdown("### Drawdown")
        dd_series = (port_val / port_val.cummax() - 1.0) * 100
        st.line_chart(dd_series.to_frame("Drawdown (%)"), use_container_width=True)

    with cB:
        st.markdown("### Correlation Matrix (returns)")
        st.dataframe(corr_matrix(prices), use_container_width=True)

        st.markdown("### Portfolio vs Strategy (value)")
        compare = pd.DataFrame({"Portfolio": port_val, "Strategy": strat_val})
        st.line_chart(compare, use_container_width=True)

