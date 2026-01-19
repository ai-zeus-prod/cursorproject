#!/usr/bin/env python3
"""
Display analysis results without needing the dashboard
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import get_db
from loguru import logger

def main():
    db = get_db()

    print("\n" + "=" * 80)
    print(" " * 20 + "INVESTMENT ANALYSIS RESULTS")
    print("=" * 80 + "\n")

    # Portfolio Stats
    print("📊 PORTFOLIO STATISTICS")
    print("-" * 80)
    stats = db.get_portfolio_stats()
    print(f"Total Trades:     {stats['total_trades']}")
    print(f"Wins:             {stats['wins']}")
    print(f"Losses:           {stats['losses']}")
    print(f"Win Rate:         {stats['win_rate']:.1f}%")
    print(f"Avg Win:          {stats['avg_win_percent']:.1f}%")
    print(f"Avg Loss:         {stats['avg_loss_percent']:.1f}%")
    print(f"Total P&L:        ₹{stats['total_pnl']:,.2f}")
    print()

    # Top Opportunities
    print("🎯 TOP OPPORTUNITIES")
    print("-" * 80)
    opportunities = db.get_top_opportunities(min_score=75, limit=10)

    if not opportunities.empty:
        for idx, opp in opportunities.iterrows():
            print(f"\n{idx + 1}. {opp['symbol']} - {opp.get('company_name', 'N/A')}")
            print(f"   Score: {opp['total_score']:.0f}/100 (F:{opp.get('fundamental_score', 0):.0f} T:{opp.get('technical_score', 0):.0f})")
            print(f"   Sector: {opp.get('sector', 'N/A')}")
            print(f"   Recommendation: {opp.get('recommendation', 'N/A')}")
            print(f"   Confidence: {opp.get('confidence', 0):.0%}")
            if opp.get('pattern_matched'):
                print(f"   Pattern: {opp['pattern_matched'].replace('_', ' ').title()}")
            print(f"   Reasoning: {opp.get('reasoning', 'N/A')}")
    else:
        print("No opportunities found yet.")
        print()
        print("💡 To generate opportunities:")
        print("   1. Run: python3 agents/agent_1_data_collector.py --test")
        print("   2. Run: python3 agents/agent_2_fundamental.py --test")
        print("   3. Run: python3 agents/agent_3_technical.py --test")
        print("   4. Run: python3 agents/agent_6_orchestrator.py --test")
        print()
        print("   Or all at once: python3 scripts/run_all_agents.py --test")

    print()

    # Open Positions
    print("💼 OPEN POSITIONS")
    print("-" * 80)
    positions = db.get_open_positions()

    if not positions.empty:
        for idx, pos in positions.iterrows():
            stock_id = db.get_stock_id(pos['symbol'])
            current_price = db.get_latest_price(stock_id)

            if current_price:
                pnl = (current_price - pos['entry_price']) * pos['quantity']
                pnl_pct = ((current_price - pos['entry_price']) / pos['entry_price']) * 100

                status = "🎯 TARGET!" if pnl_pct >= 20 else "⚠️ STOP!" if pnl_pct <= -7 else "📊 OK"

                print(f"\n{pos['symbol']} - {pos.get('company_name', 'N/A')}")
                print(f"   Entry: ₹{pos['entry_price']:.2f} | Current: ₹{current_price:.2f}")
                print(f"   Quantity: {pos['quantity']} | P&L: ₹{pnl:.2f} ({pnl_pct:+.1f}%) {status}")
    else:
        print("No open positions.")

    print()

    # Stocks in Database
    print("📚 STOCKS IN DATABASE")
    print("-" * 80)
    stocks = db.get_all_stocks()
    print(f"Total stocks: {len(stocks)}")

    if not stocks.empty:
        print("\nStock list:")
        for idx, stock in stocks.head(20).iterrows():
            print(f"  • {stock['symbol']:15s} {stock.get('company_name', 'N/A')[:40]}")
        if len(stocks) > 20:
            print(f"  ... and {len(stocks) - 20} more")

    print()
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
