"""
Agent 6: Decision Orchestrator
Combines fundamental and technical analysis to generate investment recommendations
"""

import argparse
from datetime import datetime
from typing import Dict, Optional
from loguru import logger

from config.settings import settings
from database.db_manager import get_db
from utils.pattern_matcher import PatternMatcher
from agents.agent_2_fundamental import FundamentalAnalysisAgent
from agents.agent_3_technical import TechnicalAnalysisAgent


class OrchestratorAgent:
    """Orchestrates analysis and generates investment decisions"""

    def __init__(self):
        self.db = get_db()
        self.rules = settings.load_investment_rules()
        self.scoring_rules = self.rules.get('scoring', {})
        self.fundamental_agent = FundamentalAnalysisAgent()
        self.technical_agent = TechnicalAnalysisAgent()
        self.pattern_matcher = PatternMatcher()

    def run(self, test_mode: bool = False):
        """
        Main execution method for the agent

        Args:
            test_mode: If True, only process first 3 stocks
        """
        start_time = datetime.now()
        logger.info("=" * 60)
        logger.info("AGENT 6: DECISION ORCHESTRATOR - Starting")
        logger.info("=" * 60)

        # Get all active stocks
        stocks_df = self.db.get_all_stocks(active_only=True)

        if test_mode:
            stocks_df = stocks_df.head(3)

        stocks_processed = 0
        opportunities_found = 0
        errors = []

        for _, stock in stocks_df.iterrows():
            try:
                stock_id = stock['id']
                symbol = stock['symbol']

                logger.info(f"Evaluating {symbol}...")

                # Generate complete analysis and recommendation
                analysis = self._analyze_stock(stock_id, symbol)

                if analysis:
                    # Save to database
                    self._save_analysis(stock_id, analysis)

                    # Log results
                    logger.info(f"  ✓ Total Score: {analysis['total_score']:.0f}/100")
                    logger.info(f"  📊 Recommendation: {analysis['recommendation']}")

                    if analysis['recommendation'] == 'BUY':
                        opportunities_found += 1
                        logger.info(f"  🎯 OPPORTUNITY DETECTED!")

                    stocks_processed += 1
                else:
                    logger.warning(f"  ⚠ Could not complete analysis")

            except Exception as e:
                error_msg = f"{symbol}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"✗ Error evaluating {symbol}: {str(e)}")

        # Log completion
        duration = (datetime.now() - start_time).total_seconds()

        logger.info("=" * 60)
        logger.info(f"DECISION ORCHESTRATION COMPLETE")
        logger.info(f"Evaluated: {stocks_processed}/{len(stocks_df)} stocks")
        logger.info(f"Opportunities Found: {opportunities_found}")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info("=" * 60)

        # Log to database
        self.db.log_agent_run(
            agent_name="Orchestrator",
            status="SUCCESS" if len(errors) == 0 else "FAILED",
            duration=duration,
            records=stocks_processed,
            error="\n".join(errors) if errors else None,
            details=f"Opportunities: {opportunities_found}"
        )

        return stocks_processed, opportunities_found, errors

    def _analyze_stock(self, stock_id: int, symbol: str) -> Optional[Dict]:
        """
        Perform complete analysis on a stock

        Returns:
            Dictionary with analysis results
        """
        # Get fundamental data and score
        fundamental_data = self.db.get_fundamental_data(stock_id)
        if not fundamental_data:
            return None

        fundamental_score = self.fundamental_agent._calculate_fundamental_score(fundamental_data)

        # Get technical indicators
        price_df = self.db.get_price_data(stock_id, days=365)
        if price_df.empty or len(price_df) < 50:
            return None

        technical_indicators = self.db.get_technical_indicators(stock_id)
        if not technical_indicators:
            return None

        technical_score = self.technical_agent._calculate_technical_score(price_df, technical_indicators)

        # Detect patterns
        patterns = self.pattern_matcher.find_all_patterns(price_df)

        # Calculate total score
        total_score = self._calculate_total_score(
            fundamental_score,
            technical_score,
            sentiment_score=50  # Placeholder for sentiment
        )

        # Generate recommendation
        recommendation = self._generate_recommendation(
            total_score,
            fundamental_score,
            technical_score,
            patterns
        )

        # Build reasoning
        reasoning = self._build_reasoning(
            fundamental_data,
            technical_indicators,
            patterns,
            fundamental_score,
            technical_score
        )

        # Pattern info
        pattern_matched = patterns[0]['pattern'] if patterns else None
        pattern_confidence = patterns[0]['confidence'] if patterns else None

        return {
            'fundamental_score': fundamental_score,
            'technical_score': technical_score,
            'sentiment_score': 50,  # Placeholder
            'total_score': total_score,
            'recommendation': recommendation,
            'confidence': self._calculate_confidence(fundamental_score, technical_score, patterns),
            'pattern_matched': pattern_matched,
            'pattern_confidence': pattern_confidence,
            'reasoning': reasoning,
            'date': datetime.now().strftime('%Y-%m-%d')
        }

    def _calculate_total_score(self, fundamental_score: float,
                               technical_score: float,
                               sentiment_score: float = 50) -> float:
        """Calculate weighted total score"""
        f_weight = self.scoring_rules.get('fundamental_weight', 0.5)
        t_weight = self.scoring_rules.get('technical_weight', 0.3)
        s_weight = self.scoring_rules.get('sentiment_weight', 0.2)

        total = (fundamental_score * f_weight +
                technical_score * t_weight +
                sentiment_score * s_weight)

        return total

    def _generate_recommendation(self, total_score: float,
                                fundamental_score: float,
                                technical_score: float,
                                patterns: list) -> str:
        """
        Generate BUY/HOLD/SELL/PASS recommendation

        Logic:
        - BUY: High total score + both fundamentals and technicals pass
        - HOLD: Moderate score or mixed signals
        - PASS: Low score or fails key criteria
        """
        min_total_score = self.scoring_rules.get('min_total_score', 75)
        high_conviction_score = self.scoring_rules.get('high_conviction_score', 85)

        # Minimum thresholds
        min_fundamental = 60
        min_technical = 60

        if total_score >= high_conviction_score:
            if fundamental_score >= min_fundamental and technical_score >= min_technical:
                return 'BUY'

        if total_score >= min_total_score:
            if fundamental_score >= min_fundamental and technical_score >= min_technical:
                # Check if we have supporting patterns
                if patterns:
                    return 'BUY'
                return 'HOLD'

        if total_score >= 60:
            return 'HOLD'

        return 'PASS'

    def _calculate_confidence(self, fundamental_score: float,
                             technical_score: float,
                             patterns: list) -> float:
        """Calculate confidence level (0-1)"""
        # Base confidence on score alignment
        score_diff = abs(fundamental_score - technical_score)

        if score_diff < 10:
            base_confidence = 0.8
        elif score_diff < 20:
            base_confidence = 0.7
        elif score_diff < 30:
            base_confidence = 0.6
        else:
            base_confidence = 0.5

        # Boost confidence if patterns detected
        if patterns:
            pattern_boost = max([p['confidence'] for p in patterns]) * 0.2
            base_confidence = min(0.95, base_confidence + pattern_boost)

        return base_confidence

    def _build_reasoning(self, fundamental_data: Dict,
                        technical_indicators: Dict,
                        patterns: list,
                        fundamental_score: float,
                        technical_score: float) -> str:
        """Build human-readable reasoning for the recommendation"""
        reasons = []

        # Fundamental reasoning
        if fundamental_score >= 80:
            reasons.append("Strong fundamentals")
        elif fundamental_score >= 60:
            reasons.append("Acceptable fundamentals")
        else:
            reasons.append("Weak fundamentals")

        # Key metrics
        roe = fundamental_data.get('roe')
        if roe and roe > 20:
            reasons.append(f"excellent ROE ({roe:.1f}%)")

        pe_ratio = fundamental_data.get('pe_ratio')
        if pe_ratio and pe_ratio < 20:
            reasons.append(f"attractive P/E ({pe_ratio:.1f})")

        # Technical reasoning
        if technical_score >= 80:
            reasons.append("strong technical setup")
        elif technical_score >= 60:
            reasons.append("positive technicals")

        rsi = technical_indicators.get('rsi')
        if rsi:
            if 45 <= rsi <= 65:
                reasons.append(f"healthy RSI ({rsi:.0f})")
            elif rsi < 30:
                reasons.append("oversold (potential bounce)")

        # Pattern reasoning
        if patterns:
            pattern_names = [p['pattern'].replace('_', ' ').title() for p in patterns]
            reasons.append(f"patterns detected: {', '.join(pattern_names)}")

        return "; ".join(reasons).capitalize()

    def _save_analysis(self, stock_id: int, analysis: Dict):
        """Save analysis results to database"""
        self.db.save_analysis_score(stock_id, analysis['date'], analysis)


def main():
    """Command-line entry point"""
    parser = argparse.ArgumentParser(description='Decision Orchestrator Agent')
    parser.add_argument('--test', action='store_true', help='Run in test mode (3 stocks only)')
    args = parser.parse_args()

    agent = OrchestratorAgent()
    agent.run(test_mode=args.test)


if __name__ == "__main__":
    main()
