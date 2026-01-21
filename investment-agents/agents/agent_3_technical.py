"""
Agent 3: Technical Analysis
Analyzes technical indicators and identifies patterns
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import argparse
from datetime import datetime
from typing import Dict, Optional
from loguru import logger

from config.settings import settings
from database.db_manager import get_db
from utils.technical_indicators import TechnicalIndicators
from utils.pattern_matcher import PatternMatcher


class TechnicalAnalysisAgent:
    """Analyzes technical indicators and patterns"""

    def __init__(self):
        self.db = get_db()
        self.rules = settings.load_investment_rules()
        self.technical_rules = self.rules.get('technical', {})
        self.ti = TechnicalIndicators()
        self.pm = PatternMatcher()

    def run(self, test_mode: bool = False):
        """
        Main execution method for the agent

        Args:
            test_mode: If True, only process first 3 stocks
        """
        start_time = datetime.now()
        logger.info("=" * 60)
        logger.info("AGENT 3: TECHNICAL ANALYSIS - Starting")
        logger.info("=" * 60)

        # Get all active stocks
        stocks_df = self.db.get_all_stocks(active_only=True)

        if test_mode:
            stocks_df = stocks_df.head(3)

        stocks_processed = 0
        errors = []

        for _, stock in stocks_df.iterrows():
            try:
                stock_id = stock['id']
                symbol = stock['symbol']

                logger.info(f"Analyzing {symbol}...")

                # Get price data
                price_df = self.db.get_price_data(stock_id, days=365)

                if not price_df.empty and len(price_df) >= 50:
                    # Calculate indicators
                    indicators = self.ti.get_latest_indicators(price_df)

                    if indicators:
                        # Save indicators to database
                        date_str = indicators['date'].strftime('%Y-%m-%d') if 'date' in indicators else datetime.now().strftime('%Y-%m-%d')
                        self.db.save_technical_indicators(stock_id, date_str, indicators)

                        # Calculate technical score
                        score = self._calculate_technical_score(price_df, indicators)

                        # Detect patterns
                        patterns = self.pm.find_all_patterns(price_df)

                        logger.info(f"  ✓ Technical Score: {score:.0f}/100")
                        if patterns:
                            logger.info(f"  📊 Patterns detected: {len(patterns)}")
                            for pattern in patterns:
                                logger.info(f"    - {pattern['pattern']} (confidence: {pattern['confidence']:.0%})")

                        stocks_processed += 1
                    else:
                        logger.warning(f"  ⚠ Could not calculate indicators")
                else:
                    logger.warning(f"  ⚠ Insufficient price data (need 50+ days)")

            except Exception as e:
                error_msg = f"{symbol}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"✗ Error analyzing {symbol}: {str(e)}")

        # Log completion
        duration = (datetime.now() - start_time).total_seconds()

        logger.info("=" * 60)
        logger.info(f"TECHNICAL ANALYSIS COMPLETE")
        logger.info(f"Analyzed: {stocks_processed}/{len(stocks_df)} stocks")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info("=" * 60)

        # Log to database
        self.db.log_agent_run(
            agent_name="TechnicalAnalysis",
            status="SUCCESS" if len(errors) == 0 else "FAILED",
            duration=duration,
            records=stocks_processed,
            error="\n".join(errors) if errors else None
        )

        return stocks_processed, errors

    def _calculate_technical_score(self, price_df, indicators: Dict) -> float:
        """
        Calculate technical score (0-100) based on indicators

        Scoring breakdown:
        - MA Position & Trend (25 points)
        - RSI (20 points)
        - MACD (15 points)
        - Volume (15 points)
        - Momentum (15 points)
        - Bollinger Bands (10 points)
        """
        score = 0

        # MA Position & Trend (25 points)
        ma_trend = self.ti.check_ma_trend(price_df)

        if ma_trend.get('price_above_ma_50') and ma_trend.get('price_above_ma_200'):
            score += 15  # Above both MAs
        elif ma_trend.get('price_above_ma_50'):
            score += 10  # Above 50-day

        if ma_trend.get('ma_50_trending_up'):
            score += 5
        if ma_trend.get('ma_200_trending_up'):
            score += 5

        # Golden cross bonus
        if ma_trend.get('golden_cross'):
            score += 5

        # RSI Score (20 points)
        rsi = indicators.get('rsi')
        if rsi:
            min_rsi = self.technical_rules.get('min_rsi', 45)
            max_rsi = self.technical_rules.get('max_rsi', 65)

            if min_rsi <= rsi <= max_rsi:  # Ideal range
                score += 20
            elif 40 <= rsi < min_rsi or max_rsi < rsi <= 70:  # Acceptable
                score += 15
            elif 30 <= rsi < 40 or 70 < rsi <= 80:  # Warning zone
                score += 8
            elif rsi < 30:  # Oversold (could be opportunity)
                score += 10
            else:  # Overbought
                score += 3

        # MACD Score (15 points)
        macd = indicators.get('macd')
        macd_signal = indicators.get('macd_signal')

        if macd is not None and macd_signal is not None:
            if macd > macd_signal and macd > 0:  # Bullish and above zero
                score += 15
            elif macd > macd_signal:  # Just turned bullish
                score += 12
            elif macd > 0:  # Above zero line
                score += 8
            elif macd > macd_signal:  # Turning positive
                score += 5

        # Volume Score (15 points)
        volume_ratio = indicators.get('volume_ratio')
        if volume_ratio:
            min_vol_ratio = self.technical_rules.get('min_volume_ratio', 1.5)

            if volume_ratio >= min_vol_ratio * 1.5:  # Very high volume
                score += 15
            elif volume_ratio >= min_vol_ratio:  # Above average
                score += 12
            elif volume_ratio >= 1.0:  # Normal
                score += 8
            else:  # Below average
                score += 4

        # Momentum Score (15 points)
        momentum_score = self.ti.calculate_momentum_score(price_df)
        score += (momentum_score / 100) * 15

        # Bollinger Bands Score (10 points)
        close = indicators.get('close')
        bb_upper = indicators.get('bollinger_upper')
        bb_lower = indicators.get('bollinger_lower')

        if close and bb_upper and bb_lower:
            bb_position = (close - bb_lower) / (bb_upper - bb_lower)

            if 0.3 <= bb_position <= 0.7:  # Middle of bands
                score += 10
            elif 0.2 <= bb_position < 0.3:  # Lower middle (potential bounce)
                score += 8
            elif bb_position < 0.2:  # Near lower band
                score += 6
            elif bb_position > 0.8:  # Near upper band (overbought)
                score += 3

        return min(100, score)


def main():
    """Command-line entry point"""
    parser = argparse.ArgumentParser(description='Technical Analysis Agent')
    parser.add_argument('--test', action='store_true', help='Run in test mode (3 stocks only)')
    args = parser.parse_args()

    agent = TechnicalAnalysisAgent()
    agent.run(test_mode=args.test)


if __name__ == "__main__":
    main()
