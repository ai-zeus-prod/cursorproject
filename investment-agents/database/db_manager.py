"""
Database Manager for Investment Agent System
Handles all database operations using SQLAlchemy
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime, date
import pandas as pd
from loguru import logger
from contextlib import contextmanager

from config.settings import settings


class DatabaseManager:
    """Manages database connections and operations"""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize database manager"""
        self.db_path = db_path or settings.DATABASE_PATH
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()

    def _initialize_database(self):
        """Create database and tables if they don't exist"""
        schema_path = Path(__file__).parent / "schema.sql"

        with self.get_connection() as conn:
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
                conn.executescript(schema_sql)
            conn.commit()

        logger.info(f"Database initialized at {self.db_path}")

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    # ===== STOCK OPERATIONS =====

    def add_stock(self, symbol: str, company_name: str = None,
                  sector: str = None, industry: str = None) -> int:
        """Add a new stock to the database"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                """INSERT OR IGNORE INTO stocks (symbol, company_name, sector, industry)
                   VALUES (?, ?, ?, ?)""",
                (symbol, company_name, sector, industry)
            )
            conn.commit()

            # Get the stock ID
            cursor = conn.execute("SELECT id FROM stocks WHERE symbol = ?", (symbol,))
            row = cursor.fetchone()
            return row[0] if row else None

    def get_stock_id(self, symbol: str) -> Optional[int]:
        """Get stock ID by symbol"""
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT id FROM stocks WHERE symbol = ?", (symbol,))
            row = cursor.fetchone()
            return row[0] if row else None

    def get_all_stocks(self, active_only: bool = True) -> pd.DataFrame:
        """Get all stocks from database"""
        query = "SELECT * FROM stocks"
        if active_only:
            query += " WHERE active = 1"

        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn)

    # ===== PRICE DATA OPERATIONS =====

    def save_price_data(self, stock_id: int, price_df: pd.DataFrame):
        """Save price data for a stock"""
        price_df = price_df.copy()
        price_df['stock_id'] = stock_id

        with self.get_connection() as conn:
            price_df.to_sql('price_data', conn, if_exists='append',
                           index=False, method='replace')
            conn.commit()

    def get_price_data(self, stock_id: int, days: int = 365) -> pd.DataFrame:
        """Get historical price data for a stock"""
        query = """
            SELECT date, open, high, low, close, volume, adj_close
            FROM price_data
            WHERE stock_id = ?
            ORDER BY date DESC
            LIMIT ?
        """

        with self.get_connection() as conn:
            df = pd.read_sql_query(query, conn, params=(stock_id, days))
            df['date'] = pd.to_datetime(df['date'])
            return df.sort_values('date')

    def get_latest_price(self, stock_id: int) -> Optional[float]:
        """Get the latest closing price for a stock"""
        query = """
            SELECT close FROM price_data
            WHERE stock_id = ?
            ORDER BY date DESC
            LIMIT 1
        """

        with self.get_connection() as conn:
            cursor = conn.execute(query, (stock_id,))
            row = cursor.fetchone()
            return row[0] if row else None

    # ===== FUNDAMENTAL DATA OPERATIONS =====

    def save_fundamental_data(self, stock_id: int, data: Dict[str, Any]):
        """Save fundamental data for a stock"""
        with self.get_connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO fundamental_data
                   (stock_id, quarter, year, revenue, net_income, eps, pe_ratio,
                    pb_ratio, roe, debt_equity, profit_margin, revenue_growth,
                    earnings_growth, free_cash_flow)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (stock_id, data.get('quarter'), data.get('year'),
                 data.get('revenue'), data.get('net_income'), data.get('eps'),
                 data.get('pe_ratio'), data.get('pb_ratio'), data.get('roe'),
                 data.get('debt_equity'), data.get('profit_margin'),
                 data.get('revenue_growth'), data.get('earnings_growth'),
                 data.get('free_cash_flow'))
            )
            conn.commit()

    def get_fundamental_data(self, stock_id: int) -> Optional[Dict]:
        """Get latest fundamental data for a stock"""
        query = """
            SELECT * FROM fundamental_data
            WHERE stock_id = ?
            ORDER BY collected_date DESC
            LIMIT 1
        """

        with self.get_connection() as conn:
            cursor = conn.execute(query, (stock_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    # ===== TECHNICAL INDICATORS OPERATIONS =====

    def save_technical_indicators(self, stock_id: int, date: str, indicators: Dict):
        """Save technical indicators for a stock"""
        with self.get_connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO technical_indicators
                   (stock_id, date, ma_50, ma_200, rsi, macd, macd_signal,
                    bollinger_upper, bollinger_lower, volume_sma_20, volume_ratio)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (stock_id, date, indicators.get('ma_50'), indicators.get('ma_200'),
                 indicators.get('rsi'), indicators.get('macd'), indicators.get('macd_signal'),
                 indicators.get('bollinger_upper'), indicators.get('bollinger_lower'),
                 indicators.get('volume_sma_20'), indicators.get('volume_ratio'))
            )
            conn.commit()

    def get_technical_indicators(self, stock_id: int, date: str = None) -> Optional[Dict]:
        """Get technical indicators for a stock on a specific date"""
        if date is None:
            query = """
                SELECT * FROM technical_indicators
                WHERE stock_id = ?
                ORDER BY date DESC
                LIMIT 1
            """
            params = (stock_id,)
        else:
            query = """
                SELECT * FROM technical_indicators
                WHERE stock_id = ? AND date = ?
            """
            params = (stock_id, date)

        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None

    # ===== ANALYSIS SCORES OPERATIONS =====

    def save_analysis_score(self, stock_id: int, date: str, scores: Dict):
        """Save analysis scores for a stock"""
        with self.get_connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO analysis_scores
                   (stock_id, date, fundamental_score, technical_score, sentiment_score,
                    total_score, recommendation, confidence, pattern_matched,
                    pattern_confidence, reasoning)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (stock_id, date, scores.get('fundamental_score'),
                 scores.get('technical_score'), scores.get('sentiment_score'),
                 scores.get('total_score'), scores.get('recommendation'),
                 scores.get('confidence'), scores.get('pattern_matched'),
                 scores.get('pattern_confidence'), scores.get('reasoning'))
            )
            conn.commit()

    def get_top_opportunities(self, min_score: float = 75, limit: int = 10) -> pd.DataFrame:
        """Get top scoring stocks from latest analysis"""
        query = """
            SELECT
                s.symbol, s.company_name, s.sector,
                a.date, a.fundamental_score, a.technical_score,
                a.total_score, a.recommendation, a.confidence,
                a.pattern_matched, a.reasoning
            FROM analysis_scores a
            JOIN stocks s ON a.stock_id = s.id
            WHERE a.date = (SELECT MAX(date) FROM analysis_scores)
              AND a.total_score >= ?
            ORDER BY a.total_score DESC
            LIMIT ?
        """

        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn, params=(min_score, limit))

    # ===== PORTFOLIO OPERATIONS =====

    def add_position(self, stock_id: int, entry_date: str, entry_price: float,
                    quantity: int, stop_loss: float, target_price: float) -> int:
        """Add a new position to portfolio"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO portfolio
                   (stock_id, entry_date, entry_price, quantity, stop_loss, target_price)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (stock_id, entry_date, entry_price, quantity, stop_loss, target_price)
            )
            conn.commit()
            return cursor.lastrowid

    def close_position(self, position_id: int, exit_date: str,
                      exit_price: float, exit_reason: str):
        """Close a position"""
        with self.get_connection() as conn:
            # Get position details
            cursor = conn.execute(
                "SELECT entry_date, entry_price, quantity FROM portfolio WHERE id = ?",
                (position_id,)
            )
            row = cursor.fetchone()

            if row:
                entry_date, entry_price, quantity = row
                profit_loss = (exit_price - entry_price) * quantity
                profit_loss_percent = ((exit_price - entry_price) / entry_price) * 100

                # Calculate holding days
                entry_dt = datetime.strptime(entry_date, "%Y-%m-%d")
                exit_dt = datetime.strptime(exit_date, "%Y-%m-%d")
                holding_days = (exit_dt - entry_dt).days

                # Update position
                conn.execute(
                    """UPDATE portfolio
                       SET status = 'CLOSED', exit_date = ?, exit_price = ?,
                           exit_reason = ?, profit_loss = ?, profit_loss_percent = ?,
                           holding_days = ?
                       WHERE id = ?""",
                    (exit_date, exit_price, exit_reason, profit_loss,
                     profit_loss_percent, holding_days, position_id)
                )
                conn.commit()

    def get_open_positions(self) -> pd.DataFrame:
        """Get all open positions"""
        query = """
            SELECT
                p.id, s.symbol, s.company_name,
                p.entry_date, p.entry_price, p.quantity,
                p.stop_loss, p.target_price
            FROM portfolio p
            JOIN stocks s ON p.stock_id = s.id
            WHERE p.status = 'OPEN'
            ORDER BY p.entry_date DESC
        """

        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn)

    def get_portfolio_stats(self) -> Dict:
        """Get portfolio statistics"""
        with self.get_connection() as conn:
            # Total positions
            cursor = conn.execute("SELECT COUNT(*) FROM portfolio WHERE status = 'CLOSED'")
            total_trades = cursor.fetchone()[0]

            # Win rate
            cursor = conn.execute(
                "SELECT COUNT(*) FROM portfolio WHERE status = 'CLOSED' AND profit_loss > 0"
            )
            wins = cursor.fetchone()[0]

            # Average win/loss
            cursor = conn.execute(
                "SELECT AVG(profit_loss_percent) FROM portfolio WHERE status = 'CLOSED' AND profit_loss > 0"
            )
            avg_win = cursor.fetchone()[0] or 0

            cursor = conn.execute(
                "SELECT AVG(profit_loss_percent) FROM portfolio WHERE status = 'CLOSED' AND profit_loss < 0"
            )
            avg_loss = cursor.fetchone()[0] or 0

            # Total P&L
            cursor = conn.execute(
                "SELECT SUM(profit_loss) FROM portfolio WHERE status = 'CLOSED'"
            )
            total_pnl = cursor.fetchone()[0] or 0

            win_rate = (wins / total_trades * 100) if total_trades > 0 else 0

            return {
                'total_trades': total_trades,
                'wins': wins,
                'losses': total_trades - wins,
                'win_rate': win_rate,
                'avg_win_percent': avg_win,
                'avg_loss_percent': avg_loss,
                'total_pnl': total_pnl
            }

    # ===== ALERT OPERATIONS =====

    def create_alert(self, stock_id: int, alert_type: str,
                    alert_level: str, message: str):
        """Create a new alert"""
        with self.get_connection() as conn:
            conn.execute(
                """INSERT INTO alerts (stock_id, alert_type, alert_level, message)
                   VALUES (?, ?, ?, ?)""",
                (stock_id, alert_type, alert_level, message)
            )
            conn.commit()

    def get_unread_alerts(self) -> pd.DataFrame:
        """Get all unread alerts"""
        query = """
            SELECT
                a.id, s.symbol, a.alert_type, a.alert_level,
                a.message, a.triggered_date
            FROM alerts a
            JOIN stocks s ON a.stock_id = s.id
            WHERE a.is_read = 0
            ORDER BY a.triggered_date DESC
        """

        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn)

    def mark_alerts_read(self, alert_ids: List[int]):
        """Mark alerts as read"""
        with self.get_connection() as conn:
            placeholders = ','.join('?' * len(alert_ids))
            conn.execute(
                f"UPDATE alerts SET is_read = 1 WHERE id IN ({placeholders})",
                alert_ids
            )
            conn.commit()

    # ===== AGENT RUN LOGGING =====

    def log_agent_run(self, agent_name: str, status: str,
                     duration: float = None, records: int = None,
                     error: str = None, details: str = None):
        """Log an agent run"""
        with self.get_connection() as conn:
            conn.execute(
                """INSERT INTO agent_runs
                   (agent_name, status, duration_seconds, records_processed,
                    error_message, details)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (agent_name, status, duration, records, error, details)
            )
            conn.commit()


# Global database instance
_db_instance = None

def get_db() -> DatabaseManager:
    """Get or create database instance (singleton pattern)"""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager()
    return _db_instance
