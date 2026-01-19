"""
Test script to verify system setup
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from database.db_manager import get_db
from utils.data_fetcher import DataFetcher
from utils.notifier import Notifier
from loguru import logger


def test_database():
    """Test database connection"""
    logger.info("Testing database connection...")
    try:
        db = get_db()
        stocks = db.get_all_stocks()
        logger.info(f"✓ Database OK - {len(stocks)} stocks in database")
        return True
    except Exception as e:
        logger.error(f"✗ Database error: {str(e)}")
        return False


def test_data_fetcher():
    """Test data fetching"""
    logger.info("Testing data fetcher...")
    try:
        fetcher = DataFetcher()
        price = fetcher.get_current_price("TCS.NS")
        if price:
            logger.info(f"✓ Data fetcher OK - TCS.NS price: ₹{price:.2f}")
            return True
        else:
            logger.warning("⚠ Could not fetch price (might be market hours)")
            return True  # Don't fail test if market is closed
    except Exception as e:
        logger.error(f"✗ Data fetcher error: {str(e)}")
        return False


def test_notifications():
    """Test notification system"""
    logger.info("Testing notifications...")
    try:
        notifier = Notifier()

        if settings.EMAIL_NOTIFICATIONS_ENABLED:
            logger.info("Email notifications enabled - attempting test email...")
            success = notifier.test_notification()
            if success:
                logger.info("✓ Test email sent successfully")
                return True
            else:
                logger.warning("⚠ Email notifications configured but test failed")
                return False
        else:
            logger.info("✓ Notifications OK (disabled in settings)")
            return True
    except Exception as e:
        logger.error(f"✗ Notification error: {str(e)}")
        return False


def test_config():
    """Test configuration"""
    logger.info("Testing configuration...")
    try:
        watchlist = settings.load_watchlist()
        rules = settings.load_investment_rules()

        logger.info(f"✓ Configuration OK")
        logger.info(f"  - Watchlist: {len(watchlist)} stocks")
        logger.info(f"  - Paper Trading: {settings.PAPER_TRADING_MODE}")
        logger.info(f"  - Database: {settings.DATABASE_TYPE}")
        return True
    except Exception as e:
        logger.error(f"✗ Configuration error: {str(e)}")
        return False


def main():
    """Run all tests"""
    logger.info("=" * 60)
    logger.info("SYSTEM TEST")
    logger.info("=" * 60)

    tests = [
        ("Configuration", test_config),
        ("Database", test_database),
        ("Data Fetcher", test_data_fetcher),
        ("Notifications", test_notifications),
    ]

    results = []
    for test_name, test_func in tests:
        logger.info(f"\n--- Testing {test_name} ---")
        result = test_func()
        results.append((test_name, result))
        logger.info("")

    # Summary
    logger.info("=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status} - {test_name}")

    logger.info("=" * 60)
    logger.info(f"Result: {passed}/{total} tests passed")
    logger.info("=" * 60)

    if passed == total:
        logger.info("\n🎉 All tests passed! System is ready to use.")
        logger.info("\nNext steps:")
        logger.info("1. Run agents: python scripts/run_all_agents.py --test")
        logger.info("2. Start dashboard: streamlit run dashboard/app.py")
    else:
        logger.warning("\n⚠ Some tests failed. Please check configuration.")


if __name__ == "__main__":
    main()
