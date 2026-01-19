"""
Agent 2: Fundamental Analysis
Analyzes fundamental metrics and scores stocks
"""

import argparse
from datetime import datetime
from typing import Dict, Optional
from loguru import logger

from config.settings import settings
from database.db_manager import get_db


class FundamentalAnalysisAgent:
    """Analyzes fundamental metrics and generates scores"""

    def __init__(self):
        self.db = get_db()
        self.rules = settings.load_investment_rules()
        self.fundamental_rules = self.rules.get('fundamental', {})

    def run(self, test_mode: bool = False):
        """
        Main execution method for the agent

        Args:
            test_mode: If True, only process first 3 stocks
        """
        start_time = datetime.now()
        logger.info("=" * 60)
        logger.info("AGENT 2: FUNDAMENTAL ANALYSIS - Starting")
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

                # Get fundamental data
                fundamental_data = self.db.get_fundamental_data(stock_id)

                if fundamental_data:
                    # Calculate fundamental score
                    score = self._calculate_fundamental_score(fundamental_data)

                    logger.info(f"  ✓ Fundamental Score: {score:.0f}/100")
                    stocks_processed += 1
                else:
                    logger.warning(f"  ⚠ No fundamental data available")

            except Exception as e:
                error_msg = f"{symbol}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"✗ Error analyzing {symbol}: {str(e)}")

        # Log completion
        duration = (datetime.now() - start_time).total_seconds()

        logger.info("=" * 60)
        logger.info(f"FUNDAMENTAL ANALYSIS COMPLETE")
        logger.info(f"Analyzed: {stocks_processed}/{len(stocks_df)} stocks")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info("=" * 60)

        # Log to database
        self.db.log_agent_run(
            agent_name="FundamentalAnalysis",
            status="SUCCESS" if len(errors) == 0 else "FAILED",
            duration=duration,
            records=stocks_processed,
            error="\n".join(errors) if errors else None
        )

        return stocks_processed, errors

    def _calculate_fundamental_score(self, data: Dict) -> float:
        """
        Calculate fundamental score (0-100) based on investment rules

        Scoring breakdown:
        - ROE (20 points)
        - P/E Ratio (20 points)
        - Debt/Equity (15 points)
        - Revenue Growth (15 points)
        - Profit Margin (15 points)
        - Earnings Growth (15 points)
        """
        score = 0

        # ROE Score (20 points)
        roe = data.get('roe')
        if roe:
            min_roe = self.fundamental_rules.get('min_roe', 15)
            if roe >= min_roe * 2:  # Excellent (30%+)
                score += 20
            elif roe >= min_roe * 1.5:  # Good (22.5%+)
                score += 15
            elif roe >= min_roe:  # Acceptable (15%+)
                score += 10
            elif roe >= min_roe * 0.7:  # Below target
                score += 5

        # P/E Ratio Score (20 points)
        pe_ratio = data.get('pe_ratio')
        if pe_ratio:
            max_pe = self.fundamental_rules.get('max_pe', 30)
            if 10 <= pe_ratio <= 20:  # Ideal range
                score += 20
            elif 20 < pe_ratio <= max_pe:  # Acceptable
                score += 15
            elif pe_ratio < 10:  # Might be value trap, but could be good
                score += 12
            elif pe_ratio > max_pe:  # Overvalued
                score += 5

        # Debt/Equity Score (15 points)
        debt_equity = data.get('debt_equity')
        if debt_equity is not None:
            max_de = self.fundamental_rules.get('max_debt_equity', 0.5)
            if debt_equity <= max_de * 0.5:  # Very low debt (< 0.25)
                score += 15
            elif debt_equity <= max_de:  # Low debt (< 0.5)
                score += 12
            elif debt_equity <= max_de * 1.5:  # Moderate debt
                score += 8
            elif debt_equity <= max_de * 2:  # High debt
                score += 4

        # Revenue Growth Score (15 points)
        revenue_growth = data.get('revenue_growth')
        if revenue_growth:
            min_growth = self.fundamental_rules.get('min_revenue_growth', 15)
            if revenue_growth >= min_growth * 2:  # Exceptional (30%+)
                score += 15
            elif revenue_growth >= min_growth * 1.5:  # Strong (22.5%+)
                score += 12
            elif revenue_growth >= min_growth:  # Good (15%+)
                score += 10
            elif revenue_growth >= min_growth * 0.5:  # Moderate
                score += 6
            elif revenue_growth > 0:  # Positive
                score += 3

        # Profit Margin Score (15 points)
        profit_margin = data.get('profit_margin')
        if profit_margin:
            min_margin = self.fundamental_rules.get('min_profit_margin', 10)
            if profit_margin >= min_margin * 2:  # Excellent (20%+)
                score += 15
            elif profit_margin >= min_margin * 1.5:  # Good (15%+)
                score += 12
            elif profit_margin >= min_margin:  # Acceptable (10%+)
                score += 9
            elif profit_margin >= min_margin * 0.5:  # Below target
                score += 5

        # Earnings Growth Score (15 points)
        earnings_growth = data.get('earnings_growth')
        if earnings_growth:
            if earnings_growth >= 30:  # Exceptional
                score += 15
            elif earnings_growth >= 20:  # Strong
                score += 12
            elif earnings_growth >= 15:  # Good
                score += 10
            elif earnings_growth >= 10:  # Moderate
                score += 7
            elif earnings_growth > 0:  # Positive
                score += 4

        return score

    def get_investment_philosophy_scores(self, data: Dict) -> Dict[str, float]:
        """
        Score stock against different investment philosophies

        Returns:
            Dictionary with scores for each philosophy (Buffett, Lynch, O'Neil)
        """
        scores = {}

        # Warren Buffett Score (focus on quality and value)
        buffett_score = 0
        roe = data.get('roe', 0)
        pe_ratio = data.get('pe_ratio')
        debt_equity = data.get('debt_equity', 999)

        if roe >= 20:
            buffett_score += 30
        if pe_ratio and pe_ratio < 20:
            buffett_score += 25
        if debt_equity < 0.3:
            buffett_score += 25
        if data.get('profit_margin', 0) > 15:
            buffett_score += 20

        scores['buffett'] = buffett_score

        # Peter Lynch Score (focus on PEG ratio and growth)
        lynch_score = 0
        peg = None

        if pe_ratio and data.get('earnings_growth'):
            peg = pe_ratio / data['earnings_growth']

        if peg and peg < 1:
            lynch_score += 40
        elif peg and peg < 1.5:
            lynch_score += 30

        if data.get('revenue_growth', 0) > 15:
            lynch_score += 30
        if data.get('debt_equity', 999) < 0.5:
            lynch_score += 30

        scores['lynch'] = lynch_score

        # William O'Neil Score (focus on growth and momentum)
        oneil_score = 0

        if data.get('earnings_growth', 0) >= 25:
            oneil_score += 35
        if data.get('revenue_growth', 0) >= 25:
            oneil_score += 35
        if roe > 17:
            oneil_score += 30

        scores['oneil'] = oneil_score

        return scores


def main():
    """Command-line entry point"""
    parser = argparse.ArgumentParser(description='Fundamental Analysis Agent')
    parser.add_argument('--test', action='store_true', help='Run in test mode (3 stocks only)')
    args = parser.parse_args()

    agent = FundamentalAnalysisAgent()
    agent.run(test_mode=args.test)


if __name__ == "__main__":
    main()
