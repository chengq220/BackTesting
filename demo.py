import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import date, timedelta
from simulation import Simulation
 
# ----------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------
st.set_page_config(page_title="Backtesting Dashboard", layout="wide", page_icon="📈")
 
st.title("Backtesting Dashboard")
st.caption("Enter one or more tickers, pick a strategy, and see how it would have performed historically.")
 
# ----------------------------------------------------------------------
# ============  🔌 BACKEND INTEGRATION POINT  ===========================
# Replace the inside of this function with a real call to your API.
# Keep the return shape the same and the rest of the app needs no changes.
#
# Expected return shape:
# {
#     "AAPL": {
#         "dates": ["2023-01-03", "2023-01-04", ...],
#         "portfolio_value": [10000, 10050, ...],   # strategy equity curve
#         "buy_hold_value": [10000, 10020, ...],    # baseline equity curve
#         "metrics": {
#             "total_return": 0.184,      # as a decimal, e.g. 0.184 = 18.4%
#             "cagr": 0.091,
#             "volatility": 0.22,
#             "sharpe_ratio": 1.12,
#             "max_drawdown": -0.15,
#             "win_rate": 0.54,
#             "calmar_ratio": 0.61,
#         }
#     },
#     # ...one entry per ticker, plus an optional "PORTFOLIO" key if you
#     # combine multiple tickers into one equal-weight backtest.
# }
# ========================================================================
 
def call_backtest_api(tickers, start_date, end_date, initial_capital,
                       strategy, strategy_params, combine_portfolio):
    """
    TODO: replace this mock implementation with a real request, e.g.:
 
        import requests
        resp = requests.post("https://your-api.example.com/backtest", json={
            "tickers": tickers,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "initial_capital": initial_capital,
            "strategy": strategy,
            "strategy_params": strategy_params,
            "combine_portfolio": combine_portfolio,
        })
        resp.raise_for_status()
        return resp.json()
    """
    dates = pd.date_range(start_date, end_date, freq="B")
    n = len(dates)
    rng = np.random.default_rng(seed=abs(hash(tuple(tickers))) % (2**32))
 
    results = {}
    combined_curve = np.zeros(n)
    combined_bh = np.zeros(n)
 
    for t in tickers:
        drift = rng.uniform(0.0002, 0.0006)
        vol = rng.uniform(0.01, 0.02)
        strat_returns = rng.normal(drift, vol, n)
        bh_returns = rng.normal(drift * 0.8, vol, n)
 
        strat_curve = initial_capital * np.cumprod(1 + strat_returns)
        bh_curve = initial_capital * np.cumprod(1 + bh_returns)
 
        combined_curve += strat_curve
        combined_bh += bh_curve
 
        running_max = np.maximum.accumulate(strat_curve)
        drawdown = strat_curve / running_max - 1
 
        results[t] = {
            "dates": dates.strftime("%Y-%m-%d").tolist(),
            "portfolio_value": strat_curve.tolist(),
            "buy_hold_value": bh_curve.tolist(),
            "metrics": {
                "total_return": strat_curve[-1] / strat_curve[0] - 1,
                "cagr": (strat_curve[-1] / strat_curve[0]) ** (252 / n) - 1,
                "volatility": np.std(strat_returns) * np.sqrt(252),
                "sharpe_ratio": (np.mean(strat_returns) / np.std(strat_returns)) * np.sqrt(252),
                "max_drawdown": drawdown.min(),
                "win_rate": (strat_returns > 0).mean(),
                "calmar_ratio": abs(((strat_curve[-1] / strat_curve[0]) ** (252 / n) - 1) / drawdown.min())
                                if drawdown.min() != 0 else np.nan,
            },
        }
 
    if combine_portfolio and len(tickers) > 1:
        running_max = np.maximum.accumulate(combined_curve)
        drawdown = combined_curve / running_max - 1
        combined_returns = np.diff(combined_curve) / combined_curve[:-1]
        results["PORTFOLIO"] = {
            "dates": dates.strftime("%Y-%m-%d").tolist(),
            "portfolio_value": combined_curve.tolist(),
            "buy_hold_value": combined_bh.tolist(),
            "metrics": {
                "total_return": combined_curve[-1] / combined_curve[0] - 1,
                "cagr": (combined_curve[-1] / combined_curve[0]) ** (252 / n) - 1,
                "volatility": np.std(combined_returns) * np.sqrt(252),
                "sharpe_ratio": (np.mean(combined_returns) / np.std(combined_returns)) * np.sqrt(252),
                "max_drawdown": drawdown.min(),
                "win_rate": (combined_returns > 0).mean(),
                "calmar_ratio": abs(((combined_curve[-1] / combined_curve[0]) ** (252 / n) - 1) / drawdown.min())
                                if drawdown.min() != 0 else np.nan,
            },
        }
 
    return results
 
# ========================================================================
# ------------------------------------------------------------------------
 
# ----------------------------------------------------------------------
# Sidebar - Inputs
# ----------------------------------------------------------------------
with st.sidebar:
    st.header("Settings")
 
    tickers_input = st.text_input(
        "Ticker(s) — comma separated",
        value="AAPL, MSFT",
        help="Example: AAPL, MSFT, GOOGL"
    )
 
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start date", value=date.today() - timedelta(days=365 * 3))
    with col2:
        end_date = st.date_input("End date", value=date.today())
 
    initial_capital = st.number_input(
        "Initial capital ($)", min_value=100, value=10000, step=500
    )
 
    combine_portfolio = False
    weighting = st.radio(
        "Multi-stock allocation",
        ["Equal weight", "Compare separately"],
        help="Equal weight combines all tickers into one portfolio. "
             "Compare separately backtests and charts each ticker on its own."
    )
    combine_portfolio = (weighting == "Equal weight")
 
    st.divider()
    st.subheader("Strategy")
 
    strategy = st.selectbox(
        "Choose a strategy",
        ["Buy & Hold", "SMA Crossover", "RSI Mean Reversion"]
    )
 
    strategy_params = {}
    if strategy == "SMA Crossover":
        c1, c2 = st.columns(2)
        with c1:
            strategy_params["fast_sma"] = st.number_input("Fast SMA (days)", min_value=2, value=20)
        with c2:
            strategy_params["slow_sma"] = st.number_input("Slow SMA (days)", min_value=5, value=50)
 
    if strategy == "RSI Mean Reversion":
        strategy_params["rsi_period"] = st.number_input("RSI period", min_value=2, value=14)
        c1, c2 = st.columns(2)
        with c1:
            strategy_params["rsi_low"] = st.number_input("Buy below RSI", min_value=1, max_value=50, value=30)
        with c2:
            strategy_params["rsi_high"] = st.number_input("Sell above RSI", min_value=50, max_value=99, value=70)
 
    st.divider()
    run_button = st.button("Start Backtest", use_container_width=True, type="primary")
 
# ----------------------------------------------------------------------
# Display helpers
# ----------------------------------------------------------------------
 
def fmt_pct(x):
    return f"{x * 100:,.2f}%" if pd.notnull(x) else "N/A"
 
 
def fmt_num(x):
    return f"{x:,.2f}" if pd.notnull(x) else "N/A"
 
 
def metric_display_row(metrics):
    display_fmt = {
        "total_return": ("Total Return", fmt_pct),
        "cagr": ("CAGR", fmt_pct),
        "volatility": ("Volatility (ann.)", fmt_pct),
        "sharpe_ratio": ("Sharpe Ratio", fmt_num),
        "max_drawdown": ("Max Drawdown", fmt_pct),
        "win_rate": ("Win Rate", fmt_pct),
        "calmar_ratio": ("Calmar Ratio", fmt_num),
    }
    cols = st.columns(4)
    for i, (key, (label, fmt)) in enumerate(display_fmt.items()):
        with cols[i % 4]:
            st.metric(label, fmt(metrics.get(key, np.nan)))
 
 
def render_result_block(name, result):
    st.subheader(name)
 
    dates = pd.to_datetime(result["dates"])
    portfolio_value = pd.Series(result["portfolio_value"], index=dates)
    buy_hold_value = pd.Series(result["buy_hold_value"], index=dates)
 
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=portfolio_value.index, y=portfolio_value,
                              name=f"{strategy}", line=dict(width=3)))
    fig.add_trace(go.Scatter(x=buy_hold_value.index, y=buy_hold_value,
                              name="Buy & Hold", line=dict(dash="dot")))
    fig.update_layout(
        title=f"{name} — Portfolio Growth",
        xaxis_title="Date", yaxis_title="Portfolio Value ($)",
        hovermode="x unified", height=450,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)
 
    metric_display_row(result["metrics"])
 
    with st.expander(f"Drawdown — {name}"):
        running_max = portfolio_value.cummax()
        drawdown = portfolio_value / running_max - 1
        dd_fig = go.Figure()
        dd_fig.add_trace(go.Scatter(x=drawdown.index, y=drawdown * 100,
                                     fill="tozeroy", name="Drawdown %",
                                     line=dict(color="crimson")))
        dd_fig.update_layout(title=f"{name} Drawdown", yaxis_title="Drawdown (%)", height=300)
        st.plotly_chart(dd_fig, use_container_width=True)
 
    st.divider()
 
# ----------------------------------------------------------------------
# Main logic
# ----------------------------------------------------------------------
if run_button:
    tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
 
    if not tickers:
        st.error("Please enter at least one ticker.")
        st.stop()
 
    if start_date >= end_date:
        st.error("Start date must be before end date.")
        st.stop()
 
    sim = Simulation(tickers, strategy, strategy_params, initial_capital)
    with st.spinner("Running backtest..."):
        results = call_backtest_api(
            tickers=tickers,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            strategy=strategy,
            strategy_params=strategy_params,
            combine_portfolio=combine_portfolio,
        )
 
    if not results:
        st.error("No results returned from backend.")
        st.stop()
 
    if "PORTFOLIO" in results:
        render_result_block("Combined Portfolio", results["PORTFOLIO"])
        with st.expander("Per-ticker breakdown"):
            for t in tickers:
                if t in results:
                    st.line_chart(pd.Series(
                        results[t]["portfolio_value"],
                        index=pd.to_datetime(results[t]["dates"])
                    ), height=200)
    else:
        for t in tickers:
            if t in results:
                render_result_block(t, results[t])
            else:
                st.warning(f"No result returned for '{t}'.")
 
else:
    st.info("Set your parameters in the sidebar and click **Run Backtest** to get started.")
