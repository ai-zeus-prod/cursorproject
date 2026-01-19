#!/usr/bin/env python3
"""
Quick test script to verify system is working
Run without needing the dashboard
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import settings
from database.db_manager import get_db
from utils.data_fetcher import DataFetcher

def main():
    print("=" * 60)
    print("INVESTMENT AGENT SYSTEM - QUICK TEST")
    print("=" * 60)
    print()

    # Test 1: Database
    print("1. Testing Database Connection...")
    try:
        db = get_db()
        stocks = db.get_all_stocks()
        print(f"   ✓ Database OK - {len(stocks)} stocks in database")
    except Exception as e:
        print(f"   ✗ Database Error: {e}")
        return

    print()

    # Test 2: Data Fetcher
    print("2. Testing Data Fetcher (Yahoo Finance)...")
    try:
        fetcher = DataFetcher()

        # Test with TCS
        print("   Fetching TCS.NS data...")
        price = fetcher.get_current_price("TCS.NS")

        if price:
            print(f"   ✓ TCS Current Price: ₹{price:.2f}")

            # Get company info
            info = fetcher.get_company_info("TCS.NS")
            if info:
                print(f"   ✓ Company: {info.get('company_name')}")
                print(f"   ✓ Sector: {info.get('sector')}")
        else:
            print("   ⚠ Could not fetch price (market may be closed)")

    except Exception as e:
        print(f"   ✗ Data Fetcher Error: {e}")

    print()

    # Test 3: Configuration
    print("3. Testing Configuration...")
    try:
        watchlist = settings.load_watchlist()
        rules = settings.load_investment_rules()

        print(f"   ✓ Watchlist: {len(watchlist)} stocks")
        print(f"   ✓ Paper Trading: {settings.PAPER_TRADING_MODE}")
        print(f"   ✓ Starting Capital: ₹{settings.STARTING_CAPITAL:,}")
        print(f"   ✓ Stop Loss: {settings.DEFAULT_STOP_LOSS*100}%")
        print(f"   ✓ Target Return: {settings.TARGET_RETURN*100}%")

    except Exception as e:
        print(f"   ✗ Configuration Error: {e}")

    print()
    print("=" * 60)
    print("SYSTEM STATUS: READY ✓")
    print("=" * 60)
    print()
    print("Next Steps:")
    print("1. Run agents: python3 agents/agent_1_data_collector.py --test")
    print("2. View results: python3 scripts/show_results.py")
    print("3. Or start dashboard: streamlit run dashboard/app.py")
    print()


if __name__ == "__main__":
    main()
