"""
Data fetcher for stock market data
Uses yfinance for free stock data access
"""

import yfinance as yf
import pandas as pd
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from loguru import logger

from config.settings import settings


class DataFetcher:
    """Fetches stock data from various sources"""

    def __init__(self):
        self.use_yahoo = settings.USE_YAHOO_FINANCE

    def get_price_history(self, symbol: str, period: str = "1y",
                         interval: str = "1d") -> Optional[pd.DataFrame]:
        """
        Get historical price data for a stock

        Args:
            symbol: Stock ticker symbol (e.g., 'TCS.NS')
            period: Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max')
            interval: Data interval ('1d', '1wk', '1mo')

        Returns:
            DataFrame with OHLCV data
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval)

            if hist.empty:
                logger.warning(f"No price data found for {symbol}")
                return None

            # Rename columns to match our schema
            hist = hist.reset_index()
            hist.columns = [col.lower() for col in hist.columns]

            # Ensure we have the required columns
            required_cols = ['date', 'open', 'high', 'low', 'close', 'volume']
            if not all(col in hist.columns for col in required_cols):
                logger.error(f"Missing required columns in price data for {symbol}")
                return None

            return hist[required_cols]

        except Exception as e:
            logger.error(f"Error fetching price history for {symbol}: {str(e)}")
            return None

    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current/latest price for a stock"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.history(period="1d")

            if info.empty:
                return None

            return info['Close'].iloc[-1]

        except Exception as e:
            logger.error(f"Error fetching current price for {symbol}: {str(e)}")
            return None

    def get_fundamental_data(self, symbol: str) -> Optional[Dict]:
        """
        Get fundamental data for a stock

        Returns key metrics like P/E, ROE, Debt/Equity, etc.
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            # Extract key fundamental metrics
            fundamentals = {
                'pe_ratio': info.get('trailingPE'),
                'pb_ratio': info.get('priceToBook'),
                'roe': info.get('returnOnEquity'),
                'debt_equity': info.get('debtToEquity'),
                'profit_margin': info.get('profitMargins'),
                'revenue_growth': info.get('revenueGrowth'),
                'earnings_growth': info.get('earningsGrowth'),
                'market_cap': info.get('marketCap'),
                'enterprise_value': info.get('enterpriseValue'),
                'free_cash_flow': info.get('freeCashflow'),
                'operating_cash_flow': info.get('operatingCashflow'),
                'total_revenue': info.get('totalRevenue'),
                'net_income': info.get('netIncomeToCommon'),
                'eps': info.get('trailingEps'),
                'book_value': info.get('bookValue'),
                'current_ratio': info.get('currentRatio'),
                'quick_ratio': info.get('quickRatio'),
                'dividend_yield': info.get('dividendYield'),
            }

            # Convert percentages to actual percentages (yfinance returns decimals)
            if fundamentals.get('roe'):
                fundamentals['roe'] = fundamentals['roe'] * 100
            if fundamentals.get('profit_margin'):
                fundamentals['profit_margin'] = fundamentals['profit_margin'] * 100
            if fundamentals.get('revenue_growth'):
                fundamentals['revenue_growth'] = fundamentals['revenue_growth'] * 100
            if fundamentals.get('earnings_growth'):
                fundamentals['earnings_growth'] = fundamentals['earnings_growth'] * 100
            if fundamentals.get('dividend_yield'):
                fundamentals['dividend_yield'] = fundamentals['dividend_yield'] * 100

            # Convert debt_to_equity if it's in the wrong format
            if fundamentals.get('debt_equity') and fundamentals['debt_equity'] > 100:
                fundamentals['debt_equity'] = fundamentals['debt_equity'] / 100

            return fundamentals

        except Exception as e:
            logger.error(f"Error fetching fundamental data for {symbol}: {str(e)}")
            return None

    def get_company_info(self, symbol: str) -> Optional[Dict]:
        """Get basic company information"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            return {
                'symbol': symbol,
                'company_name': info.get('longName') or info.get('shortName'),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'market_cap': info.get('marketCap'),
                'website': info.get('website'),
                'description': info.get('longBusinessSummary'),
                'employees': info.get('fullTimeEmployees'),
                'country': info.get('country'),
            }

        except Exception as e:
            logger.error(f"Error fetching company info for {symbol}: {str(e)}")
            return None

    def get_earnings_history(self, symbol: str) -> Optional[pd.DataFrame]:
        """Get earnings history for a stock"""
        try:
            ticker = yf.Ticker(symbol)
            earnings = ticker.earnings

            if earnings is None or earnings.empty:
                logger.warning(f"No earnings data found for {symbol}")
                return None

            return earnings

        except Exception as e:
            logger.error(f"Error fetching earnings history for {symbol}: {str(e)}")
            return None

    def get_quarterly_earnings(self, symbol: str) -> Optional[pd.DataFrame]:
        """Get quarterly earnings for a stock"""
        try:
            ticker = yf.Ticker(symbol)
            earnings = ticker.quarterly_earnings

            if earnings is None or earnings.empty:
                logger.warning(f"No quarterly earnings data found for {symbol}")
                return None

            return earnings

        except Exception as e:
            logger.error(f"Error fetching quarterly earnings for {symbol}: {str(e)}")
            return None

    def get_batch_prices(self, symbols: List[str]) -> Dict[str, float]:
        """Get current prices for multiple stocks efficiently"""
        prices = {}

        for symbol in symbols:
            price = self.get_current_price(symbol)
            if price:
                prices[symbol] = price

        return prices

    def validate_symbol(self, symbol: str) -> bool:
        """Check if a stock symbol is valid"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            # Check if we got valid data
            return 'regularMarketPrice' in info or 'currentPrice' in info

        except Exception:
            return False
