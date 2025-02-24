-- Add these tables to your existing database if they don't already exist
-- This ensures all data needed for the dashboard is properly stored

-- Table for market data (if not already exists)
CREATE TABLE IF NOT EXISTS market_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chain TEXT NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    current_price REAL,
    volume REAL,
    price_change_percentage_24h REAL,
    market_cap REAL,
    market_cap_rank INTEGER,
    total_supply REAL,
    max_supply REAL,
    circulating_supply REAL,
    ath REAL,
    ath_change_percentage REAL,
    UNIQUE(chain, timestamp)
);
CREATE INDEX IF NOT EXISTS idx_market_data_chain_timestamp ON market_data(chain, timestamp);

-- Table for mood data
CREATE TABLE IF NOT EXISTS mood_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chain TEXT NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    mood TEXT NOT NULL,
    price_change REAL,
    trading_volume REAL,
    volatility REAL,
    social_sentiment REAL,
    funding_rates REAL,
    liquidation_volume REAL,
    UNIQUE(chain, timestamp)
);
CREATE INDEX IF NOT EXISTS idx_mood_data_chain_timestamp ON mood_data(chain, timestamp);

-- Table for correlation analysis
CREATE TABLE IF NOT EXISTS correlation_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    price_correlation REAL,
    volume_correlation REAL,
    market_cap_ratio REAL
);
CREATE INDEX IF NOT EXISTS idx_correlation_data_timestamp ON correlation_data(timestamp);

-- Table for posted content
CREATE TABLE IF NOT EXISTS posted_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    content TEXT NOT NULL,
    sentiment TEXT,
    trigger_type TEXT,
    price_data TEXT,
    meme_phrases TEXT
);
CREATE INDEX IF NOT EXISTS idx_posted_content_timestamp ON posted_content(timestamp);

-- Add some helper views for the dashboard
CREATE VIEW IF NOT EXISTS v_recent_market_data AS
SELECT chain, 
       current_price,
       volume,
       price_change_percentage_24h,
       timestamp
FROM market_data
WHERE timestamp >= datetime('now', '-1 day')
ORDER BY chain, timestamp DESC;

-- View for daily statistics
CREATE VIEW IF NOT EXISTS v_daily_stats AS
SELECT chain,
       date(timestamp) as date,
       avg(current_price) as avg_price,
       max(current_price) as max_price,
       min(current_price) as min_price,
       avg(volume) as avg_volume
FROM market_data
GROUP BY chain, date(timestamp)
ORDER BY chain, date DESC;
