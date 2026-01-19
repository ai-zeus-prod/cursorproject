# Detailed Setup Guide

Step-by-step instructions to get your Investment Agent System running.

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Installation Steps](#installation-steps)
3. [Configuration](#configuration)
4. [First Run](#first-run)
5. [Scheduling Agents](#scheduling-agents)
6. [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements
- **OS**: Linux, macOS, or Windows 10+
- **Python**: 3.9 or higher
- **RAM**: 2GB available
- **Disk**: 500MB free space
- **Internet**: Broadband connection

### Recommended
- **RAM**: 4GB+ for smoother operation
- **Disk**: 1GB+ for historical data storage

## Installation Steps

### Step 1: Verify Python Installation

```bash
python --version
# Should show Python 3.9.x or higher
```

If Python is not installed:
- **Windows**: Download from python.org
- **macOS**: `brew install python3`
- **Linux**: `sudo apt install python3 python3-pip`

### Step 2: Set Up Virtual Environment

```bash
cd investment-agents

# Create virtual environment
python -m venv venv

# Activate it
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Verify activation (you should see (venv) in prompt)
which python  # Should point to venv/bin/python
```

### Step 3: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt

# This may take 2-5 minutes
```

**Common Issues:**
- If `pandas-ta` fails: `pip install pandas-ta --no-cache-dir`
- If `ta-lib` fails: This is optional, system will work without it

### Step 4: Configure Environment

```bash
# Copy example configuration
cp .env.example .env

# Edit with your preferred editor
nano .env
# or
vim .env
# or open in VS Code
code .env
```

**Minimum Configuration (for testing):**
```bash
USER_NAME=YourName
USER_EMAIL=your.email@example.com
PAPER_TRADING_MODE=True
EMAIL_NOTIFICATIONS_ENABLED=False  # Enable later
```

### Step 5: Customize Watchlist

Edit `config/watchlist.json`:

```json
{
  "stocks": [
    "TCS.NS",       # NSE: Tata Consultancy Services
    "INFY.NS",      # NSE: Infosys
    "HDFCBANK.NS",  # NSE: HDFC Bank
    "RELIANCE.NS"   # NSE: Reliance Industries
  ]
}
```

**Stock Symbol Format:**
- NSE stocks: Add `.NS` suffix (e.g., `TCS.NS`)
- BSE stocks: Add `.BO` suffix (e.g., `TCS.BO`)
- US stocks: No suffix (e.g., `AAPL`)

### Step 6: Initialize Database

```bash
python scripts/setup_database.py
```

**Expected Output:**
```
==============================================================
DATABASE SETUP
==============================================================
Creating database at: ./data/investment_agents.db
✓ Database schema created successfully
✓ Tables created: 13
  - agent_runs
  - alerts
  - analysis_scores
  - fundamental_data
  - portfolio
  - price_data
  - stocks
  - system_settings
  - technical_indicators
  - trade_history
  - agent_learning
==============================================================
DATABASE SETUP COMPLETE!
==============================================================
```

## Configuration

### Email Notifications (Optional)

To receive morning briefings and alerts:

1. **For Gmail:**
   - Go to https://myaccount.google.com/security
   - Enable 2-Factor Authentication
   - Generate App Password: https://myaccount.google.com/apppasswords
   - Use app password (not your regular password)

2. **Update .env:**
```bash
EMAIL_NOTIFICATIONS_ENABLED=True
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your.email@gmail.com
SMTP_PASSWORD=your_16_char_app_password
```

3. **Test:**
```bash
python -c "
from utils.notifier import Notifier
n = Notifier()
n.test_notification()
"
```

### Investment Rules

Edit `config/investment_rules.json` to match your strategy:

**Conservative (Lower Risk):**
```json
{
  "fundamental": {
    "min_roe": 20,
    "max_pe": 25,
    "max_debt_equity": 0.3
  },
  "technical": {
    "min_rsi": 45,
    "max_rsi": 60
  },
  "scoring": {
    "min_total_score": 80
  }
}
```

**Aggressive (Higher Risk/Reward):**
```json
{
  "fundamental": {
    "min_roe": 15,
    "max_pe": 35,
    "max_debt_equity": 0.7
  },
  "technical": {
    "min_rsi": 40,
    "max_rsi": 70
  },
  "scoring": {
    "min_total_score": 70
  }
}
```

## First Run

### Step 1: System Test

```bash
python scripts/test_system.py
```

**Expected: All tests should pass**
```
=============================================================
TEST SUMMARY
=============================================================
✓ PASS - Configuration
✓ PASS - Database
✓ PASS - Data Fetcher
✓ PASS - Notifications
=============================================================
Result: 4/4 tests passed
=============================================================
```

### Step 2: Run Agents (Test Mode)

```bash
# This will process only 3 stocks (fast)
python scripts/run_all_agents.py --test
```

**What happens:**
1. Agent 1 fetches data for 3 stocks (~30 seconds)
2. Agent 2 analyzes fundamentals (~10 seconds)
3. Agent 3 analyzes technicals (~10 seconds)
4. Agent 6 generates recommendations (~5 seconds)

**Expected Output:**
```
🤖 Running Agent 1: Data Collector...
Processing TCS.NS...
✓ TCS.NS updated successfully
...
Opportunities Found: 1-2
```

### Step 3: Launch Dashboard

```bash
streamlit run dashboard/app.py
```

**Browser will open automatically at http://localhost:8501**

Explore:
- 🎯 Top Opportunities: See recommended stocks
- 💼 Portfolio: (empty initially - add positions manually or via agent)
- 📊 Recent Activity: Agent run history

### Step 4: Full Run (All Stocks)

Once test mode works:

```bash
# This will process your full watchlist
python scripts/run_all_agents.py

# With email notification
python scripts/run_all_agents.py --notify
```

Processing time: ~2-5 minutes for 20 stocks

## Scheduling Agents

### Option 1: Manual Daily Execution

Create a simple script `daily_run.sh`:

```bash
#!/bin/bash
cd /path/to/investment-agents
source venv/bin/activate
python scripts/run_all_agents.py --notify
```

Run every morning manually.

### Option 2: Cron Job (Linux/macOS)

```bash
# Edit crontab
crontab -e

# Add these lines (adjust paths):
# Data collection at 7:00 AM
0 7 * * * cd /path/to/investment-agents && /path/to/venv/bin/python agents/agent_1_data_collector.py

# Analysis at 7:30 AM
30 7 * * * cd /path/to/investment-agents && /path/to/venv/bin/python agents/agent_2_fundamental.py
30 7 * * * cd /path/to/investment-agents && /path/to/venv/bin/python agents/agent_3_technical.py

# Recommendations at 8:00 AM
0 8 * * * cd /path/to/investment-agents && /path/to/venv/bin/python agents/agent_6_orchestrator.py

# Morning briefing at 8:45 AM
45 8 * * * cd /path/to/investment-agents && /path/to/venv/bin/python scripts/run_all_agents.py --notify
```

### Option 3: Task Scheduler (Windows)

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily at 8:00 AM
4. Action: Start a program
   - Program: `C:\path\to\venv\Scripts\python.exe`
   - Arguments: `C:\path\to\investment-agents\scripts\run_all_agents.py --notify`
   - Start in: `C:\path\to\investment-agents`

## Troubleshooting

### Issue: "ModuleNotFoundError"

**Solution:**
```bash
# Ensure virtual environment is activated
which python  # Should point to venv

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Database is locked"

**Solution:**
```bash
# Close all Python processes
ps aux | grep python
kill <pid>

# Or restart system
```

### Issue: "No data found for symbol"

**Causes:**
- Incorrect symbol format (use .NS for NSE)
- Market is closed (data from previous day)
- Stock delisted or merged

**Solution:**
```bash
# Test individual stock
python -c "
import yfinance as yf
ticker = yf.Ticker('TCS.NS')
print(ticker.history(period='5d'))
"
```

### Issue: Dashboard shows "No opportunities"

**Causes:**
- Agents haven't run yet
- Scoring too strict
- No stocks meet criteria

**Solutions:**
1. Run agents: `python scripts/run_all_agents.py --test`
2. Lower minimum score in dashboard (slider)
3. Adjust rules in `config/investment_rules.json`

### Issue: Email notifications not sending

**Common Causes:**
- Incorrect credentials
- Using regular password instead of app password
- SMTP blocked by firewall

**Solutions:**
1. Verify credentials: `python scripts/test_system.py`
2. Generate Gmail app password
3. Check firewall settings
4. Try different SMTP port: 465 with SSL

### Issue: Agents running slow

**Causes:**
- Large watchlist
- Slow internet
- API rate limiting

**Solutions:**
1. Start with 5-10 stocks
2. Run during off-peak hours
3. Use test mode for quick iterations

## Next Steps

Once everything is working:

1. **Week 1-2: Paper Trading**
   - Run agents daily
   - Review recommendations
   - Don't make real trades yet
   - Track what would have happened

2. **Week 3-4: Strategy Tuning**
   - Adjust investment rules
   - Refine watchlist
   - Backtest changes
   - Build confidence

3. **Month 2+: Live Trading (Optional)**
   - Start with small positions (₹10,000-25,000)
   - Follow system recommendations
   - Track actual results
   - Scale gradually

## Getting Help

If you encounter issues:

1. **Check logs:** `logs/agents.log`
2. **Run tests:** `python scripts/test_system.py`
3. **Verify config:** Review `.env` and `config/*.json`
4. **Search errors:** Google the specific error message
5. **Debug mode:** Set `DEBUG=True` in `.env`

## Best Practices

1. **Backup database regularly:**
   ```bash
   cp data/investment_agents.db data/backup_$(date +%Y%m%d).db
   ```

2. **Update watchlist quarterly** based on market conditions

3. **Review agent logs weekly** for errors

4. **Keep .env secure** - never commit to git

5. **Start conservative** - use paper trading mode

---

**You're all set! 🚀 Happy investing!**
