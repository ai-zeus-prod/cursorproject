"""
Run all agents in sequence
Useful for testing or manual execution
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.agent_1_data_collector import DataCollectorAgent
from agents.agent_2_fundamental import FundamentalAnalysisAgent
from agents.agent_3_technical import TechnicalAnalysisAgent
from agents.agent_6_orchestrator import OrchestratorAgent
from utils.notifier import Notifier
from database.db_manager import get_db
from loguru import logger


def main():
    """Run all agents in sequence"""
    parser = argparse.ArgumentParser(description='Run all agents')
    parser.add_argument('--test', action='store_true', help='Run in test mode (3 stocks only)')
    parser.add_argument('--notify', action='store_true', help='Send email notification when done')
    args = parser.parse_args()

    logger.info("=" * 80)
    logger.info("RUNNING ALL AGENTS")
    logger.info("=" * 80)

    # Agent 1: Data Collection
    logger.info("\n🤖 Running Agent 1: Data Collector...")
    agent1 = DataCollectorAgent()
    stocks_collected, errors1 = agent1.run(test_mode=args.test)

    # Agent 2: Fundamental Analysis
    logger.info("\n🤖 Running Agent 2: Fundamental Analysis...")
    agent2 = FundamentalAnalysisAgent()
    stocks_analyzed_f, errors2 = agent2.run(test_mode=args.test)

    # Agent 3: Technical Analysis
    logger.info("\n🤖 Running Agent 3: Technical Analysis...")
    agent3 = TechnicalAnalysisAgent()
    stocks_analyzed_t, errors3 = agent3.run(test_mode=args.test)

    # Agent 6: Decision Orchestrator
    logger.info("\n🤖 Running Agent 6: Decision Orchestrator...")
    agent6 = OrchestratorAgent()
    stocks_evaluated, opportunities, errors6 = agent6.run(test_mode=args.test)

    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("ALL AGENTS COMPLETE - SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Data Collected: {stocks_collected} stocks")
    logger.info(f"Fundamentals Analyzed: {stocks_analyzed_f} stocks")
    logger.info(f"Technicals Analyzed: {stocks_analyzed_t} stocks")
    logger.info(f"Opportunities Found: {opportunities}")
    logger.info(f"Total Errors: {len(errors1) + len(errors2) + len(errors3) + len(errors6)}")
    logger.info("=" * 80)

    # Send notification if requested
    if args.notify:
        logger.info("\n📧 Sending notification...")
        notifier = Notifier()
        db = get_db()

        opportunities_df = db.get_top_opportunities(min_score=75, limit=5)
        portfolio_stats = db.get_portfolio_stats()

        success = notifier.send_morning_briefing(
            opportunities=opportunities_df.to_dict('records'),
            portfolio_summary=portfolio_stats
        )

        if success:
            logger.info("✓ Notification sent successfully")
        else:
            logger.warning("⚠ Failed to send notification")

    logger.info("\n✨ All done! View results at: http://localhost:8501")


if __name__ == "__main__":
    main()
