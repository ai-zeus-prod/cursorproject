"""
Database setup script
Initializes the database and loads initial configuration
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager
from config.settings import settings
from loguru import logger


def main():
    """Initialize database"""
    logger.info("=" * 60)
    logger.info("DATABASE SETUP")
    logger.info("=" * 60)

    # Create database
    logger.info(f"Creating database at: {settings.DATABASE_PATH}")
    db = DatabaseManager()

    logger.info("✓ Database schema created successfully")

    # Verify tables
    with db.get_connection() as conn:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = [row[0] for row in cursor.fetchall()]

    logger.info(f"✓ Tables created: {len(tables)}")
    for table in tables:
        logger.info(f"  - {table}")

    logger.info("=" * 60)
    logger.info("DATABASE SETUP COMPLETE!")
    logger.info("=" * 60)
    logger.info(f"\nNext steps:")
    logger.info("1. Copy .env.example to .env and configure your settings")
    logger.info("2. Update config/watchlist.json with your stocks")
    logger.info("3. Run: python agents/agent_1_data_collector.py --test")
    logger.info("4. Run: streamlit run dashboard/app.py")


if __name__ == "__main__":
    main()
