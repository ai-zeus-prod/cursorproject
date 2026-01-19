"""
Agent 1: Data Collector
Fetches and stores market data for all stocks in watchlist
"""

import argparse
from datetime import datetime, timedelta
from typing import List
from loguru import logger

from config.settings import settings
from database.db_manager import get_db
from utils.data_fetcher import DataFetcher


class DataCollectorAgent:
    """Collects and stores market data for stocks"""

    def __init__(self):
        self.db = get_db()
        self.fetcher = DataFetcher()
        self.watchlist = settings.load_watchlist()

    def run(self, test_mode: bool = False):
        """
        Main execution method for the agent

        Args:
            test_mode: If True, only process first 3 stocks
        """
        start_time = datetime.now()
        logger.info("=" * 60)
        logger.info("AGENT 1: DATA COLLECTOR - Starting")
        logger.info("=" * 60)

        stocks_processed = 0
        errors = []

        # Limit stocks in test mode
        stocks_to_process = self.watchlist[:3] if test_mode else self.watchlist

        for symbol in stocks_to_process:
            try:
                logger.info(f"Processing {symbol}...")

                # Get or create stock in database
                stock_id = self._ensure_stock_exists(symbol)

                if stock_id:
                    # Fetch and store price data
                    self._update_price_data(stock_id, symbol)

                    # Fetch and store fundamental data
                    self._update_fundamental_data(stock_id, symbol)

                    stocks_processed += 1
                    logger.info(f"✓ {symbol} updated successfully")
                else:
                    errors.append(f"{symbol}: Could not create/find stock")

            except Exception as e:
                error_msg = f"{symbol}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"✗ Error processing {symbol}: {str(e)}")

        # Log completion
        duration = (datetime.now() - start_time).total_seconds()

        logger.info("=" * 60)
        logger.info(f"DATA COLLECTION COMPLETE")
        logger.info(f"Processed: {stocks_processed}/{len(stocks_to_process)} stocks")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Errors: {len(errors)}")
        logger.info("=" * 60)

        # Log to database
        self.db.log_agent_run(
            agent_name="DataCollector",
            status="SUCCESS" if len(errors) == 0 else "FAILED",
            duration=duration,
            records=stocks_processed,
            error="\n".join(errors) if errors else None
        )

        if errors:
            logger.warning("Errors encountered:")
            for error in errors:
                logger.warning(f"  - {error}")

        return stocks_processed, errors

    def _ensure_stock_exists(self, symbol: str) -> int:
        """Ensure stock exists in database, create if needed"""
        stock_id = self.db.get_stock_id(symbol)

        if stock_id:
            return stock_id

        # Fetch company info and create stock
        logger.info(f"  Creating new stock entry for {symbol}")
        company_info = self.fetcher.get_company_info(symbol)

        if company_info:
            stock_id = self.db.add_stock(
                symbol=symbol,
                company_name=company_info.get('company_name'),
                sector=company_info.get('sector'),
                industry=company_info.get('industry')
            )
            logger.info(f"  ✓ Created stock: {company_info.get('company_name')}")
            return stock_id

        return None

    def _update_price_data(self, stock_id: int, symbol: str):
        """Fetch and store price data"""
        logger.info(f"  Fetching price data...")

        # Get last 2 years of data
        price_df = self.fetcher.get_price_history(symbol, period="2y")

        if price_df is not None and not price_df.empty:
            # Save to database
            self.db.save_price_data(stock_id, price_df)
            logger.info(f"  ✓ Saved {len(price_df)} price records")
        else:
            logger.warning(f"  ⚠ No price data available")

    def _update_fundamental_data(self, stock_id: int, symbol: str):
        """Fetch and store fundamental data"""
        logger.info(f"  Fetching fundamental data...")

        fundamentals = self.fetcher.get_fundamental_data(symbol)

        if fundamentals:
            # Add current quarter info
            now = datetime.now()
            quarter = f"Q{(now.month - 1) // 3 + 1}"
            year = now.year

            fundamentals['quarter'] = quarter
            fundamentals['year'] = year

            self.db.save_fundamental_data(stock_id, fundamentals)
            logger.info(f"  ✓ Saved fundamental data")

            # Log key metrics
            if fundamentals.get('pe_ratio'):
                logger.info(f"    P/E: {fundamentals['pe_ratio']:.2f}")
            if fundamentals.get('roe'):
                logger.info(f"    ROE: {fundamentals['roe']:.1f}%")
        else:
            logger.warning(f"  ⚠ No fundamental data available")


def main():
    """Command-line entry point"""
    parser = argparse.ArgumentParser(description='Data Collector Agent')
    parser.add_argument('--test', action='store_true', help='Run in test mode (3 stocks only)')
    args = parser.parse_args()

    agent = DataCollectorAgent()
    agent.run(test_mode=args.test)


if __name__ == "__main__":
    main()
