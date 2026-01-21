# How to Run the Investment Agent System

## 🎯 Quick Start (3 Steps)

### Step 1: Open Terminal
In VS Code: **Terminal → New Terminal**

### Step 2: Navigate to Project
```bash
cd investment-agents
```

### Step 3: Run Agents
```bash
# Test with 3 stocks (fastest)
python3 agents/agent_1_data_collector.py --test

# Or run all agents at once
python3 scripts/run_all_agents.py --test
```

---

## 📋 What Each Agent Does

### Agent 1: Data Collector
**Fetches market data from Yahoo Finance**

```bash
# Test mode (3 stocks, ~2 minutes)
python3 agents/agent_1_data_collector.py --test

# Full watchlist (20 stocks, ~10 minutes)
python3 agents/agent_1_data_collector.py
```

**What it collects:**
- 2 years of historical price data (OHLCV)
- Company fundamentals (P/E, ROE, Debt/Equity, margins)
- Company info (name, sector, industry)
- Stores everything in SQLite database

**Output:**
```
============================================================
AGENT 1: DATA COLLECTOR - Starting
============================================================
Processing TCS.NS...
  Creating new stock entry for TCS.NS
  ✓ Created stock: Tata Consultancy Services
  Fetching price data...
  ✓ Saved 500 price records
  Fetching fundamental data...
  ✓ Saved fundamental data
    P/E: 28.45
    ROE: 42.1%
✓ TCS.NS updated successfully
============================================================
DATA COLLECTION COMPLETE
Processed: 3/3 stocks
Duration: 45.23 seconds
============================================================
```

---

### Agent 2: Fundamental Analysis
**Analyzes company quality using investment frameworks**

```bash
python3 agents/agent_2_fundamental.py --test
```

**What it analyzes:**
- Warren Buffett criteria (moat, management, value)
- Peter Lynch criteria (PEG ratio, growth)
- William O'Neil CAN SLIM (earnings, new highs)
- Generates fundamental score (0-100)

**Output:**
```
============================================================
AGENT 2: FUNDAMENTAL ANALYSIS - Starting
============================================================
Analyzing TCS.NS...
  ✓ Fundamental Score: 88/100
  Framework Scores:
    - Buffett: 92/100 (Strong moat, consistent earnings)
    - Lynch: 85/100 (PEG: 1.2, reasonable growth)
    - O'Neil: 87/100 (Earnings growth: 18%)
============================================================
```

---

### Agent 3: Technical Analysis
**Calculates indicators and detects patterns**

```bash
python3 agents/agent_3_technical.py --test
```

**What it calculates:**
- Moving Averages (50-day, 200-day, EMA)
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Volume analysis
- Pattern detection (cup & handle, breakouts, etc.)

**Output:**
```
============================================================
AGENT 3: TECHNICAL ANALYSIS - Starting
============================================================
Analyzing TCS.NS...
  ✓ Technical Score: 82/100
  📊 Patterns detected: 2
    - consolidation_breakout (confidence: 75%)
    - volume_surge (confidence: 80%)
============================================================
```

---

### Agent 6: Decision Orchestrator
**Combines analysis and generates recommendations**

```bash
python3 agents/agent_6_orchestrator.py --test
```

**What it does:**
- Combines fundamental + technical scores
- Applies your investment rules
- Generates BUY/HOLD/PASS recommendations
- Provides reasoning for each decision

**Output:**
```
============================================================
AGENT 6: DECISION ORCHESTRATOR - Starting
============================================================
Evaluating TCS.NS...
  ✓ Total Score: 87/100
  📊 Recommendation: BUY
  🎯 OPPORTUNITY DETECTED!

Reasoning:
  - Strong fundamentals (88/100)
  - Excellent ROE (42.1%)
  - Positive technicals (82/100)
  - Patterns: Consolidation Breakout, Volume Surge
  - Price above 50-day and 200-day MA

Entry: ₹3,850
Stop Loss: ₹3,580 (7% risk)
Target: ₹4,620 (20% gain)
============================================================
```

---

## 🚀 Running All Agents Together

### Option 1: Run Script (Recommended)
```bash
python3 scripts/run_all_agents.py --test
```

Runs all agents in sequence:
1. Data Collector → 2. Fundamental → 3. Technical → 4. Orchestrator

**Total time:** ~3-5 minutes for 3 stocks

---

### Option 2: Manual Sequence
```bash
# Step 1: Collect data
python3 agents/agent_1_data_collector.py --test

# Step 2: Analyze fundamentals
python3 agents/agent_2_fundamental.py --test

# Step 3: Analyze technicals
python3 agents/agent_3_technical.py --test

# Step 4: Generate recommendations
python3 agents/agent_6_orchestrator.py --test
```

---

## 📊 View Results

### Option 1: Command Line
```bash
python3 scripts/show_results.py
```

Shows:
- Top opportunities with scores
- Investment recommendations
- Portfolio status
- Stocks in database

---

### Option 2: Dashboard (Recommended)
```bash
streamlit run dashboard/app.py
```

Opens interactive web dashboard at: http://localhost:8501

**Features:**
- Visual opportunity cards with scores
- Portfolio tracking with live P&L
- Charts and graphs
- Detailed stock analysis
- Historical performance

---

## ⚙️ Customization

### Edit Your Watchlist
```bash
# Edit this file
nano config/watchlist.json
```

**Add Indian stocks:**
```json
{
  "stocks": [
    "TCS.NS",        // Tata Consultancy
    "INFY.NS",       // Infosys
    "HDFCBANK.NS",   // HDFC Bank
    "RELIANCE.NS",   // Reliance
    "WIPRO.NS",      // Wipro
    "ITC.NS",        // ITC
    "SBIN.NS"        // State Bank of India
  ]
}
```

**Note:** Use `.NS` for NSE stocks, `.BO` for BSE stocks

---

### Adjust Investment Rules
```bash
nano config/investment_rules.json
```

**Key settings to adjust:**
```json
{
  "fundamental": {
    "min_roe": 15,           // Minimum Return on Equity (%)
    "max_pe": 30,            // Maximum P/E ratio
    "max_debt_equity": 0.5,  // Maximum Debt/Equity ratio
    "min_revenue_growth": 15 // Minimum revenue growth (%)
  },
  "technical": {
    "min_rsi": 45,           // RSI lower bound
    "max_rsi": 65,           // RSI upper bound
    "require_above_50ma": true,
    "require_above_200ma": true
  },
  "risk_management": {
    "default_stop_loss": 0.07,   // 7%
    "target_return": 0.20,       // 20%
    "max_position_size": 25000   // ₹25,000 per stock
  }
}
```

---

## 🔧 Troubleshooting

### "Module not found" Error
```bash
# Make sure you're in the right directory
cd investment-agents

# Check if you're in the right place
ls  # Should see: agents, config, database, utils, etc.
```

---

### "No data available" in Dashboard
```bash
# Run the data collector first
python3 agents/agent_1_data_collector.py --test

# Then run all other agents
python3 scripts/run_all_agents.py --test

# Then open dashboard
streamlit run dashboard/app.py
```

---

### Network Errors (403, timeout)
**Normal during market hours or from certain networks.**

Solutions:
- Try running at different times
- Use VPN if needed
- Yahoo Finance has rate limits

**The system stores data once collected, so you only need to fetch once per day.**

---

### Database Issues
```bash
# Reset database if needed
rm data/investment_agents.db
python3 scripts/setup_database.py

# Re-collect data
python3 agents/agent_1_data_collector.py --test
```

---

## 📅 Recommended Schedule

### Daily (9:00-9:30 AM)
```bash
# Update data (takes 2-3 minutes)
python3 agents/agent_1_data_collector.py

# Generate recommendations
python3 scripts/run_all_agents.py

# View results
streamlit run dashboard/app.py
```

---

### Weekly (Sunday Evening)
```bash
# Full analysis with all 20 stocks
python3 scripts/run_all_agents.py

# Review performance
python3 scripts/show_results.py

# Update watchlist based on findings
nano config/watchlist.json
```

---

## 🎯 Next Steps

1. **Test with 3 stocks:** `python3 scripts/run_all_agents.py --test`
2. **Review results:** `python3 scripts/show_results.py`
3. **Open dashboard:** `streamlit run dashboard/app.py`
4. **Customize watchlist:** Edit `config/watchlist.json`
5. **Adjust rules:** Edit `config/investment_rules.json`
6. **Start paper trading:** Review recommendations, track performance

---

## 💡 Tips

1. **Start small:** Use `--test` flag to process only 3 stocks
2. **Run daily:** Fresh data = better recommendations
3. **Paper trade first:** Test strategy before real money
4. **Review weekly:** Adjust rules based on performance
5. **Track results:** Use dashboard to monitor win rate
6. **Be patient:** System targets 20% over weeks/months, not days

---

## 📚 More Information

- **README.md** - Complete system overview
- **SETUP_GUIDE.md** - Detailed installation
- **QUICKSTART.md** - 5-minute guide
- **config/investment_rules.json** - All rules and thresholds

---

## ✅ Quick Reference

```bash
# Quick test (3 stocks)
python3 scripts/run_all_agents.py --test

# View results
python3 scripts/show_results.py

# Launch dashboard
streamlit run dashboard/app.py

# Full run (all stocks)
python3 scripts/run_all_agents.py
```

**That's it! Happy investing! 📈**
