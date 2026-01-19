"""
Investment Strategy Agent System - Main Dashboard
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from database.db_manager import get_db

# Page configuration
st.set_page_config(
    page_title="Investment Agent System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
db = get_db()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .opportunity-card {
        background-color: #e8f4ea;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #4CAF50;
        margin: 1rem 0;
    }
    .score-excellent {
        color: #4CAF50;
        font-weight: bold;
        font-size: 1.5rem;
    }
    .score-good {
        color: #FF9800;
        font-weight: bold;
        font-size: 1.5rem;
    }
    .score-poor {
        color: #F44336;
        font-weight: bold;
        font-size: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main dashboard page"""

    # Header
    st.markdown('<div class="main-header">📊 Investment Strategy Agent System</div>', unsafe_allow_html=True)

    # Mode indicator
    mode = "📝 PAPER TRADING" if settings.PAPER_TRADING_MODE else "💰 LIVE TRADING"
    mode_color = "blue" if settings.PAPER_TRADING_MODE else "red"

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"### Welcome, {settings.USER_NAME}!")
    with col2:
        st.markdown(f"**Mode:** :{mode_color}[{mode}]")
    with col3:
        st.markdown(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}")

    st.divider()

    # Quick Stats Row
    st.subheader("📈 Portfolio Overview")

    stats = db.get_portfolio_stats()

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            label="Total Trades",
            value=stats['total_trades']
        )

    with col2:
        st.metric(
            label="Win Rate",
            value=f"{stats['win_rate']:.1f}%"
        )

    with col3:
        st.metric(
            label="Total P&L",
            value=f"₹{stats['total_pnl']:,.0f}",
            delta=f"{stats['total_pnl']:,.0f}"
        )

    with col4:
        st.metric(
            label="Avg Win",
            value=f"{stats['avg_win_percent']:.1f}%"
        )

    with col5:
        st.metric(
            label="Avg Loss",
            value=f"{stats['avg_loss_percent']:.1f}%"
        )

    st.divider()

    # Main content area
    tab1, tab2, tab3 = st.tabs(["🎯 Top Opportunities", "💼 Open Positions", "📊 Recent Activity"])

    with tab1:
        show_opportunities()

    with tab2:
        show_open_positions()

    with tab3:
        show_recent_activity()


def show_opportunities():
    """Display top investment opportunities"""
    st.subheader("Today's Top Opportunities")

    min_score = st.slider("Minimum Score", 0, 100, 75, 5)

    opportunities = db.get_top_opportunities(min_score=min_score, limit=10)

    if not opportunities.empty:
        st.info(f"Found {len(opportunities)} opportunities with score ≥ {min_score}")

        for _, opp in opportunities.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])

                with col1:
                    st.markdown(f"### {opp['symbol']} - {opp.get('company_name', 'N/A')}")
                    st.markdown(f"**Sector:** {opp.get('sector', 'N/A')}")

                with col2:
                    score_class = (
                        "score-excellent" if opp['total_score'] >= 85 else
                        "score-good" if opp['total_score'] >= 75 else
                        "score-poor"
                    )
                    st.markdown(f'<div class="{score_class}">Score: {opp["total_score"]:.0f}/100</div>', unsafe_allow_html=True)
                    st.markdown(f"📈 Fundamental: {opp.get('fundamental_score', 0):.0f}")
                    st.markdown(f"📊 Technical: {opp.get('technical_score', 0):.0f}")

                with col3:
                    st.markdown(f"**{opp.get('recommendation', 'N/A')}**")
                    st.markdown(f"Confidence: {opp.get('confidence', 0):.0%}")

                # Reasoning
                st.markdown(f"💡 **Reasoning:** {opp.get('reasoning', 'N/A')}")

                # Pattern
                if opp.get('pattern_matched'):
                    st.markdown(f"📊 **Pattern:** {opp['pattern_matched'].replace('_', ' ').title()}")

                st.divider()
    else:
        st.warning(f"No opportunities found with score ≥ {min_score}")
        st.info("Try lowering the minimum score or running the analysis agents.")


def show_open_positions():
    """Display open portfolio positions"""
    st.subheader("Your Open Positions")

    positions = db.get_open_positions()

    if not positions.empty:
        st.info(f"You have {len(positions)} open positions")

        # Add current prices and P&L
        for idx, pos in positions.iterrows():
            stock_id = db.get_stock_id(pos['symbol'])
            current_price = db.get_latest_price(stock_id)

            if current_price:
                pnl = (current_price - pos['entry_price']) * pos['quantity']
                pnl_pct = ((current_price - pos['entry_price']) / pos['entry_price']) * 100

                col1, col2, col3, col4, col5 = st.columns(5)

                with col1:
                    st.markdown(f"**{pos['symbol']}**")
                    st.caption(pos.get('company_name', ''))

                with col2:
                    st.metric("Entry", f"₹{pos['entry_price']:.2f}")
                    st.caption(f"Qty: {pos['quantity']}")

                with col3:
                    st.metric("Current", f"₹{current_price:.2f}")

                with col4:
                    st.metric("P&L", f"₹{pnl:.2f}", f"{pnl_pct:.1f}%")

                with col5:
                    if pnl_pct <= -7:
                        st.error("⚠️ Near Stop Loss")
                    elif pnl_pct >= 20:
                        st.success("🎯 Target Reached!")
                    else:
                        st.info("📊 On Track")

                st.divider()
    else:
        st.info("No open positions. Start by exploring opportunities in the '🎯 Top Opportunities' tab.")


def show_recent_activity():
    """Show recent agent runs and alerts"""
    st.subheader("Recent System Activity")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🤖 Recent Agent Runs")

        # Query last agent runs from database
        query = "SELECT * FROM agent_runs ORDER BY run_date DESC LIMIT 5"
        with db.get_connection() as conn:
            agent_runs = pd.read_sql_query(query, conn)

        if not agent_runs.empty:
            for _, run in agent_runs.iterrows():
                status_emoji = "✅" if run['status'] == 'SUCCESS' else "❌"
                st.markdown(f"{status_emoji} **{run['agent_name']}**")
                st.caption(f"{run['run_date']} - {run.get('records_processed', 0)} records")
        else:
            st.info("No agent runs yet. Run agents to see activity.")

    with col2:
        st.markdown("#### 🔔 Recent Alerts")

        alerts = db.get_unread_alerts()

        if not alerts.empty:
            for _, alert in alerts.iterrows():
                level_emoji = {
                    'INFO': 'ℹ️',
                    'WARNING': '⚠️',
                    'CRITICAL': '🚨'
                }.get(alert['alert_level'], 'ℹ️')

                st.markdown(f"{level_emoji} **{alert['symbol']}** - {alert['alert_type']}")
                st.caption(alert['message'])
        else:
            st.success("No alerts")


# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/150x50/1f77b4/ffffff?text=Investment+Agent", use_column_width=True)

    st.markdown("### 🎛️ Quick Actions")

    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

    st.divider()

    st.markdown("### ⚙️ System Info")
    st.markdown(f"**Version:** 1.0.0")
    st.markdown(f"**Environment:** {settings.ENVIRONMENT}")
    st.markdown(f"**Database:** SQLite")

    st.divider()

    st.markdown("### 📚 Resources")
    st.markdown("[📖 Documentation](#)")
    st.markdown("[💡 Investment Philosophy](#)")
    st.markdown("[⚙️ Settings](#)")


if __name__ == "__main__":
    main()
