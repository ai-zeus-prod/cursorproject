"""
Central configuration management for Investment Agent System
Loads settings from .env and provides typed access
"""

import os
from pathlib import Path
from typing import Dict, List
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

class Settings:
    """Application settings loaded from environment"""

    # General
    APP_NAME: str = os.getenv("APP_NAME", "Investment Agent System")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Database
    DATABASE_TYPE: str = os.getenv("DATABASE_TYPE", "sqlite")
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", str(DATA_DIR / "investment_agents.db"))

    # User Info
    USER_NAME: str = os.getenv("USER_NAME", "Investor")
    USER_EMAIL: str = os.getenv("USER_EMAIL", "")
    USER_PHONE: str = os.getenv("USER_PHONE", "")
    USER_TIMEZONE: str = os.getenv("USER_TIMEZONE", "Asia/Kolkata")

    # Trading
    STARTING_CAPITAL: float = float(os.getenv("STARTING_CAPITAL", "100000"))
    MAX_POSITION_SIZE: float = float(os.getenv("MAX_POSITION_SIZE", "25000"))
    MAX_PORTFOLIO_ALLOCATION: float = float(os.getenv("MAX_PORTFOLIO_ALLOCATION", "0.70"))
    DEFAULT_STOP_LOSS: float = float(os.getenv("DEFAULT_STOP_LOSS", "0.07"))
    TARGET_RETURN: float = float(os.getenv("TARGET_RETURN", "0.20"))

    # APIs
    USE_YAHOO_FINANCE: bool = os.getenv("USE_YAHOO_FINANCE", "True").lower() == "true"
    ALPHA_VANTAGE_KEY: str = os.getenv("ALPHA_VANTAGE_KEY", "")

    # Notifications
    EMAIL_NOTIFICATIONS_ENABLED: bool = os.getenv("EMAIL_NOTIFICATIONS_ENABLED", "False").lower() == "true"
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    MORNING_BRIEF_TIME: str = os.getenv("MORNING_BRIEF_TIME", "08:45")
    EOD_REPORT_TIME: str = os.getenv("EOD_REPORT_TIME", "16:00")

    # Claude API
    CLAUDE_API_ENABLED: bool = os.getenv("CLAUDE_API_ENABLED", "False").lower() == "true"
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    # Agent Scheduling
    AGENT_1_SCHEDULE: str = os.getenv("AGENT_1_SCHEDULE", "07:00")
    AGENT_2_SCHEDULE: str = os.getenv("AGENT_2_SCHEDULE", "07:30")
    AGENT_3_SCHEDULE: str = os.getenv("AGENT_3_SCHEDULE", "07:45")
    AGENT_6_SCHEDULE: str = os.getenv("AGENT_6_SCHEDULE", "08:30")

    # Risk Management
    ENABLE_CIRCUIT_BREAKERS: bool = os.getenv("ENABLE_CIRCUIT_BREAKERS", "True").lower() == "true"
    MAX_DRAWDOWN_THRESHOLD: float = float(os.getenv("MAX_DRAWDOWN_THRESHOLD", "0.15"))
    MIN_WIN_RATE_THRESHOLD: float = float(os.getenv("MIN_WIN_RATE_THRESHOLD", "0.40"))
    MAX_CONSECUTIVE_LOSSES: int = int(os.getenv("MAX_CONSECUTIVE_LOSSES", "5"))

    # Paper Trading
    PAPER_TRADING_MODE: bool = os.getenv("PAPER_TRADING_MODE", "True").lower() == "true"

    # Advanced
    ENABLE_PATTERN_MATCHING: bool = os.getenv("ENABLE_PATTERN_MATCHING", "True").lower() == "true"
    PATTERN_LOOKBACK_DAYS: int = int(os.getenv("PATTERN_LOOKBACK_DAYS", "1825"))
    MIN_PATTERN_CONFIDENCE: float = float(os.getenv("MIN_PATTERN_CONFIDENCE", "0.65"))

    # Dashboard
    DASHBOARD_PORT: int = int(os.getenv("DASHBOARD_PORT", "8501"))
    DASHBOARD_AUTO_REFRESH: int = int(os.getenv("DASHBOARD_AUTO_REFRESH", "300"))

    # Logging
    LOG_FILE_PATH: str = os.getenv("LOG_FILE_PATH", str(LOG_DIR / "agents.log"))
    LOG_ROTATION: str = os.getenv("LOG_ROTATION", "1 week")
    LOG_RETENTION: str = os.getenv("LOG_RETENTION", "4 weeks")

    @classmethod
    def get_database_url(cls) -> str:
        """Get database connection URL"""
        if cls.DATABASE_TYPE == "sqlite":
            return f"sqlite:///{cls.DATABASE_PATH}"
        else:
            raise ValueError(f"Unsupported database type: {cls.DATABASE_TYPE}")

    @classmethod
    def load_watchlist(cls) -> List[str]:
        """Load stock watchlist from JSON"""
        watchlist_path = CONFIG_DIR / "watchlist.json"
        if watchlist_path.exists():
            with open(watchlist_path, 'r') as f:
                data = json.load(f)
                return data.get("stocks", [])
        return []

    @classmethod
    def load_investment_rules(cls) -> Dict:
        """Load investment rules from JSON"""
        rules_path = CONFIG_DIR / "investment_rules.json"
        if rules_path.exists():
            with open(rules_path, 'r') as f:
                return json.load(f)
        return cls.get_default_rules()

    @staticmethod
    def get_default_rules() -> Dict:
        """Default investment rules"""
        return {
            "fundamental": {
                "min_roe": 15,
                "max_pe": 30,
                "max_debt_equity": 0.5,
                "min_revenue_growth": 15,
                "min_profit_margin": 10
            },
            "technical": {
                "min_rsi": 45,
                "max_rsi": 65,
                "require_above_50ma": True,
                "require_above_200ma": True,
                "min_volume_ratio": 1.5
            },
            "scoring": {
                "fundamental_weight": 0.5,
                "technical_weight": 0.3,
                "sentiment_weight": 0.2,
                "min_total_score": 75
            }
        }

# Global settings instance
settings = Settings()
