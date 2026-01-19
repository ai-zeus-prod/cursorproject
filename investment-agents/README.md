# Investment Strategy & Analysis Application

AI-powered multi-agent system for systematic stock investing, combining fundamental analysis, technical signals, and pattern recognition to achieve consistent returns while minimizing downside risk.

## 🎯 Features

### Core Capabilities
- **Multi-Agent Architecture**: 6+ specialized agents working autonomously
- **Fundamental Analysis**: Applies Warren Buffett, Peter Lynch, and William O'Neil frameworks
- **Technical Analysis**: 15+ indicators including MA, RSI, MACD, Bollinger Bands
- **Pattern Recognition**: Cup & handle, consolidation breakouts, volume surges
- **Real-time Monitoring**: Automated alerts for opportunities and portfolio changes
- **Risk Management**: Built-in stop-loss, position sizing, and circuit breakers
- **Self-Learning System**: Agent 7 continuously improves recommendations
- **Paper Trading**: Safe testing mode before live trading

### Investment Philosophy
- **Target**: 20% returns with minimized downside risk
- **Approach**: Strong fundamentals + Technical momentum = High probability setups
- **Validation**: Quick price validation (days/weeks) confirms thesis strength
- **Diversification**: Sector allocation and position sizing for risk control

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Investment Agent System                   │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐      ┌──────────────┐     ┌──────────────┐
│   Agent 1    │      │   Agent 2    │     │   Agent 3    │
│     Data     │──┬──▶│ Fundamental  │──┬─▶│  Technical   │
│  Collector   │  │   │   Analysis   │  │  │   Analysis   │
└──────────────┘  │   └──────────────┘  │  └──────────────┘
                  │                     │
                  ▼                     ▼
            ┌──────────────────────────────┐
            │      Agent 6: Orchestrator    │
            │   (Decision & Scoring)        │
            └──────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Database   │ │  Dashboard   │ │ Notifications│
│   (SQLite)   │ │ (Streamlit)  │ │   (Email)    │
└──────────────┘ └──────────────┘ └──────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- 500MB disk space
- Email account for alerts (optional)
- Internet connection

### Installation

1. **Navigate to project directory**
```bash
cd investment-agents
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings (email, watchlist, etc.)
```

5. **Initialize database**
```bash
python scripts/setup_database.py
```

6. **Test system**
```bash
python scripts/test_system.py
```

7. **Run agents (test mode)**
```bash
python scripts/run_all_agents.py --test
```

8. **Launch dashboard**
```bash
streamlit run dashboard/app.py
```

Dashboard will open at: http://localhost:8501

## 📋 Configuration

### Watchlist
Edit `config/watchlist.json`:
```json
{
  "stocks": [
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "RELIANCE.NS"
  ],
  "sectors": ["IT", "Banking", "Pharma"]
}
```

### Investment Rules
Edit `config/investment_rules.json` to customize:
- Fundamental thresholds (ROE, P/E, Debt/Equity)
- Technical criteria (RSI range, MA requirements)
- Risk management (stop-loss, position sizing)
- Scoring weights

### Environment Variables
Key settings in `.env`:
```bash
# Trading
STARTING_CAPITAL=100000
MAX_POSITION_SIZE=25000
DEFAULT_STOP_LOSS=0.07
TARGET_RETURN=0.20

# Paper Trading (recommended for start)
PAPER_TRADING_MODE=True

# Email Notifications
EMAIL_NOTIFICATIONS_ENABLED=True
SMTP_USERNAME=your.email@gmail.com
SMTP_PASSWORD=your_app_password
```

## 🤖 Agent System

### Agent 1: Data Collector
- Fetches price data (Yahoo Finance)
- Collects fundamental metrics
- Updates database daily
- **Schedule**: 7:00 AM

### Agent 2: Fundamental Analysis
- Calculates fundamental scores
- Applies Buffett/Lynch/O'Neil frameworks
- Identifies quality companies
- **Schedule**: 7:30 AM

### Agent 3: Technical Analysis
- Computes 15+ technical indicators
- Detects chart patterns
- Calculates momentum scores
- **Schedule**: 7:45 AM

### Agent 6: Decision Orchestrator
- Combines fundamental + technical scores
- Generates BUY/HOLD/SELL recommendations
- Provides reasoning for decisions
- **Schedule**: 8:30 AM

### Agent 5: Portfolio Monitor
- Tracks open positions
- Triggers stop-loss/target alerts
- Validates investment thesis timeline
- **Schedule**: 4:00 PM (market close)

### Agent 7: Learning System
- Analyzes historical recommendations
- Identifies what works/doesn't work
- Auto-adjusts scoring criteria
- **Schedule**: Weekly (Sunday 8:00 PM)

## 📱 Daily Usage

### Morning Routine (9:00-9:30 AM)
1. **Check email** - Morning briefing with 3-5 opportunities
2. **Review dashboard** - Detailed analysis of recommendations
3. **Make decisions** - Execute trades based on signals
4. **15-20 minutes total**

### Evening Check (4:00-4:30 PM)
1. **Portfolio update** - End of day P&L
2. **Alert review** - Any positions needing attention
3. **5-10 minutes**

### Weekend Review (Sunday)
1. **Performance analysis** - Win rate, returns, learnings
2. **Strategy adjustments** - Update rules if needed
3. **Next week planning** - Review upcoming opportunities
4. **30-60 minutes**

## 📊 Dashboard Features

### 🎯 Opportunities Tab
- Top scoring stocks (75+ score)
- Fundamental + Technical breakdown
- Pattern detection
- Entry/exit recommendations
- Historical pattern matching

### 💼 Portfolio Tab
- Open positions with live P&L
- Days held vs target timeline
- Stop-loss and target tracking
- Performance attribution

### 📈 Research Tab
- Custom stock screeners
- Deep dive analysis
- Backtesting tools
- Sector comparison

### ⚙️ Settings Tab
- Configure rules
- Adjust scoring weights
- Update watchlist
- Test notifications

## 🛡️ Risk Management

### Built-in Protections
1. **Position Sizing**: Max 5-10% per stock
2. **Stop Loss**: Automatic 7% stops
3. **Diversification**: Max 30% per sector
4. **Circuit Breakers**: Pause at 15% drawdown
5. **Validation Timeline**: Exit if not performing in 30 days

### Paper Trading Mode
- Test strategy without real money
- Track what would have happened
- Build confidence before live trading
- **Recommended for first 1-3 months**

## 📈 Performance Tracking

### Key Metrics
- **Win Rate**: Target 60%+
- **Average Win**: Target 20%+
- **Average Loss**: Keep below 8%
- **Sharpe Ratio**: Risk-adjusted returns
- **Max Drawdown**: Largest peak-to-trough decline

### Validation Checks
- **Day 7**: Should be up 2-5%
- **Day 14**: Should be up 5-10%
- **Day 30**: Review if not progressing
- **Day 60**: Target 20% or exit

## 🔧 Maintenance

### Daily
- Agents run automatically (if scheduled)
- Check email for alerts
- Review dashboard

### Weekly
- Review performance
- Adjust watchlist if needed
- Check for errors in logs

### Monthly
- Strategy review meeting
- Update investment rules
- Backtest any changes
- Review win/loss patterns

## 🆘 Troubleshooting

### Database Issues
```bash
# Reset database
rm data/investment_agents.db
python scripts/setup_database.py
```

### Agent Not Running
```bash
# Manual agent execution
python agents/agent_1_data_collector.py --test
python agents/agent_6_orchestrator.py --test
```

### Dashboard Won't Start
```bash
# Check Streamlit
streamlit --version

# Try different port
streamlit run dashboard/app.py --server.port 8502
```

### Data Fetch Errors
- Check internet connection
- Verify stock symbols (use .NS for NSE)
- Market hours may affect real-time data
- Yahoo Finance is free but has rate limits

## 📚 Investment Resources

### Recommended Reading
- "The Intelligent Investor" - Benjamin Graham
- "One Up On Wall Street" - Peter Lynch
- "How to Make Money in Stocks" - William O'Neil

### Learning Resources
- Screener.in (Indian stocks)
- TradingView (charts)
- MoneyControl (news)
- CA Rachana Ranade (YouTube)

## 🔐 Security & Privacy

- All data stored locally (SQLite)
- No data sent to external services (except market data APIs)
- Email credentials stored in .env (never committed to git)
- Paper trading mode protects capital during testing

## 📝 License

Personal use only. Not for redistribution.

## 🤝 Support

For issues or questions:
1. Check logs: `logs/agents.log`
2. Run test script: `python scripts/test_system.py`
3. Review configuration: `.env` and `config/*.json`

## 🎯 Success Metrics

### Application Success
- Screener identifies 5-10 quality stocks weekly
- 70%+ of identified stocks show upward movement within 2 weeks
- Dashboard reduces analysis time from 2 hours to 30 minutes per stock

### Investment Success
- 60%+ win rate on trades
- Average winning trade: 20%+
- Average losing trade: <8% (stop-loss discipline)
- Overall portfolio: 20% annual return target

---

**⚠️ Disclaimer**: This system is for educational purposes. Past performance does not guarantee future results. Always conduct your own research and consider your risk tolerance before investing.

**🎉 Happy Investing!**
