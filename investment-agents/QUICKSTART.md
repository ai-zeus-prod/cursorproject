# Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites
- Python 3.9+ installed
- Internet connection

## Installation

```bash
# 1. Navigate to project directory
cd investment-agents

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# 4. Install dependencies (this takes 2-3 minutes)
pip install -r requirements.txt

# 5. Setup database
python scripts/setup_database.py

# 6. Test the system
python scripts/test_system.py

# 7. Run agents in test mode (processes 3 stocks)
python scripts/run_all_agents.py --test

# 8. Launch dashboard
streamlit run dashboard/app.py
```

## Expected Output

After step 8, your browser should open to http://localhost:8501 showing the Investment Agent System dashboard.

## What's Included

- ✅ Complete project structure
- ✅ 6 specialized agents
- ✅ Multi-framework analysis (Buffett, Lynch, O'Neil)
- ✅ Pattern recognition system
- ✅ Interactive dashboard
- ✅ Risk management framework
- ✅ Paper trading mode (safe testing)
- ✅ Email notifications (optional)

## First Steps

1. **Configure your watchlist**: Edit `config/watchlist.json`
2. **Customize rules**: Edit `config/investment_rules.json`
3. **Set your preferences**: Edit `.env` file
4. **Run in test mode** for 1-2 weeks before live trading

## Configuration Files

### Watchlist (`config/watchlist.json`)
```json
{
  "stocks": ["TCS.NS", "INFY.NS", "HDFCBANK.NS"]
}
```

### Environment (`.env`)
```bash
USER_NAME=YourName
PAPER_TRADING_MODE=True  # Keep this True initially!
EMAIL_NOTIFICATIONS_ENABLED=False  # Enable after setup
```

## Default Settings

- **Paper Trading**: ENABLED (safe mode)
- **Capital**: ₹1,00,000
- **Max Position**: ₹25,000 (5% per stock)
- **Stop Loss**: 7%
- **Target**: 20%
- **Min Score**: 75/100

## Need Help?

- **Detailed Setup**: See [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **Documentation**: See [README.md](README.md)
- **Logs**: Check `logs/agents.log`
- **Test System**: Run `python scripts/test_system.py`

## Common Issues

**"ModuleNotFoundError"**: Install dependencies
```bash
pip install -r requirements.txt
```

**"No module named pandas"**: Activate virtual environment
```bash
source venv/bin/activate  # Linux/macOS
```

**Dashboard won't start**: Check if port 8501 is in use
```bash
streamlit run dashboard/app.py --server.port 8502
```

## Next Steps

1. ✅ **Completed Setup**: System is ready!
2. 📊 **Week 1-2**: Run agents daily, observe recommendations
3. 📈 **Week 3-4**: Adjust settings based on results
4. 💰 **Month 2+**: Consider live trading (optional)

---

**🚀 You're ready to go! Start with the dashboard and explore the opportunities.**
