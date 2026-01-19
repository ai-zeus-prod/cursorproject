-- Investment Agent System Database Schema

-- Stock Master Table
CREATE TABLE IF NOT EXISTS stocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL UNIQUE,
    company_name TEXT,
    sector TEXT,
    industry TEXT,
    market_cap REAL,
    exchange TEXT DEFAULT 'NSE',
    active BOOLEAN DEFAULT 1,
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Price Data Table (Historical and Current)
CREATE TABLE IF NOT EXISTS price_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id INTEGER NOT NULL,
    date DATE NOT NULL,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume INTEGER,
    adj_close REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(id),
    UNIQUE(stock_id, date)
);

-- Fundamental Data Table
CREATE TABLE IF NOT EXISTS fundamental_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id INTEGER NOT NULL,
    quarter TEXT,
    year INTEGER,
    revenue REAL,
    net_income REAL,
    eps REAL,
    pe_ratio REAL,
    pb_ratio REAL,
    roe REAL,
    debt_equity REAL,
    profit_margin REAL,
    revenue_growth REAL,
    earnings_growth REAL,
    free_cash_flow REAL,
    collected_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(id),
    UNIQUE(stock_id, quarter, year)
);

-- Technical Indicators Table
CREATE TABLE IF NOT EXISTS technical_indicators (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id INTEGER NOT NULL,
    date DATE NOT NULL,
    ma_50 REAL,
    ma_200 REAL,
    rsi REAL,
    macd REAL,
    macd_signal REAL,
    bollinger_upper REAL,
    bollinger_lower REAL,
    volume_sma_20 REAL,
    volume_ratio REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(id),
    UNIQUE(stock_id, date)
);

-- Analysis Scores Table
CREATE TABLE IF NOT EXISTS analysis_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id INTEGER NOT NULL,
    date DATE NOT NULL,
    fundamental_score REAL,
    technical_score REAL,
    sentiment_score REAL,
    total_score REAL,
    recommendation TEXT CHECK(recommendation IN ('BUY', 'HOLD', 'SELL', 'PASS')),
    confidence REAL,
    pattern_matched TEXT,
    pattern_confidence REAL,
    reasoning TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(id),
    UNIQUE(stock_id, date)
);

-- Portfolio Holdings Table
CREATE TABLE IF NOT EXISTS portfolio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id INTEGER NOT NULL,
    entry_date DATE NOT NULL,
    entry_price REAL NOT NULL,
    quantity INTEGER NOT NULL,
    stop_loss REAL,
    target_price REAL,
    status TEXT CHECK(status IN ('OPEN', 'CLOSED')) DEFAULT 'OPEN',
    exit_date DATE,
    exit_price REAL,
    exit_reason TEXT,
    profit_loss REAL,
    profit_loss_percent REAL,
    holding_days INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(id)
);

-- Trade History Table (All trades including paper trading)
CREATE TABLE IF NOT EXISTS trade_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id INTEGER NOT NULL,
    trade_type TEXT CHECK(trade_type IN ('BUY', 'SELL')) NOT NULL,
    trade_date TIMESTAMP NOT NULL,
    price REAL NOT NULL,
    quantity INTEGER NOT NULL,
    total_value REAL NOT NULL,
    is_paper_trade BOOLEAN DEFAULT 1,
    commission REAL DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(id)
);

-- Alerts Table
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id INTEGER NOT NULL,
    alert_type TEXT NOT NULL,
    alert_level TEXT CHECK(alert_level IN ('INFO', 'WARNING', 'CRITICAL')),
    message TEXT NOT NULL,
    triggered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT 0,
    is_sent BOOLEAN DEFAULT 0,
    FOREIGN KEY (stock_id) REFERENCES stocks(id)
);

-- Agent Learning Table (For Agent 7)
CREATE TABLE IF NOT EXISTS agent_learning (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id INTEGER NOT NULL,
    recommendation_date DATE NOT NULL,
    fundamental_score REAL,
    technical_score REAL,
    pattern_matched TEXT,
    confidence REAL,
    was_traded BOOLEAN DEFAULT 0,
    entry_price REAL,
    outcome_1week REAL,
    outcome_2week REAL,
    outcome_4week REAL,
    outcome_8week REAL,
    final_result TEXT CHECK(final_result IN ('WIN', 'LOSS', 'NEUTRAL')),
    stop_hit BOOLEAN,
    target_hit BOOLEAN,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(id)
);

-- System Settings Table
CREATE TABLE IF NOT EXISTS system_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL UNIQUE,
    value TEXT NOT NULL,
    description TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Agent Run Log Table
CREATE TABLE IF NOT EXISTS agent_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name TEXT NOT NULL,
    run_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT CHECK(status IN ('SUCCESS', 'FAILED', 'RUNNING')),
    duration_seconds REAL,
    records_processed INTEGER,
    error_message TEXT,
    details TEXT
);

-- Create Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_price_data_stock_date ON price_data(stock_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_fundamental_stock ON fundamental_data(stock_id);
CREATE INDEX IF NOT EXISTS idx_technical_stock_date ON technical_indicators(stock_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_analysis_stock_date ON analysis_scores(stock_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_portfolio_status ON portfolio(status);
CREATE INDEX IF NOT EXISTS idx_alerts_unread ON alerts(is_read);
CREATE INDEX IF NOT EXISTS idx_trade_history_stock ON trade_history(stock_id, trade_date DESC);
