#!/bin/bash
# Installation script for Layer 1 Crypto Analysis Dashboard

# Exit on error
set -e

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Log helper functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check Python version
log_info "Checking Python version..."
python_version=$(python3 --version | cut -d' ' -f2)
if [[ $(echo "$python_version" | cut -d. -f1) -lt 3 ]] || [[ $(echo "$python_version" | cut -d. -f2) -lt 7 ]]; then
    log_error "Python 3.7+ is required. Found: $python_version"
    exit 1
fi
log_info "Python version $python_version is compatible."

# Check if running in the right directory
if [ ! -f "bot.py" ] || [ ! -f "config.py" ]; then
    log_warn "This script should be run from your bot's project directory."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create directories
log_info "Creating necessary directories..."
mkdir -p templates static data

# Check if database exists
if [ ! -f "data/crypto_history.db" ]; then
    log_warn "Database file not found at data/crypto_history.db"
    read -p "Create a new database? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Creating new database..."
        touch data/crypto_history.db
    else
        log_error "Database file is required to continue."
        exit 1
    fi
fi

# Install requirements
log_info "Installing required packages..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    # Create requirements.txt if it doesn't exist
    echo "# Dashboard Requirements
Flask==2.0.1
Flask-SocketIO==5.1.1
eventlet==0.33.0
python-dotenv==0.19.2
requests==2.27.1
gunicorn==20.1.0" > requirements.txt
    pip install -r requirements.txt
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    log_info "Creating .env file template..."
    cp env-template.txt .env 2>/dev/null || echo "# Environment Variables
DASHBOARD_SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(16))')
DATABASE_PATH=data/crypto_history.db" > .env
    log_warn "Please edit .env file with your actual values."
fi

# Apply database schema
log_info "Applying database schema..."
if [ -f "schema_modifications.sql" ]; then
    sqlite3 data/crypto_history.db < schema_modifications.sql
else
    # Create schema file
    echo "-- Database schema modifications
CREATE TABLE IF NOT EXISTS market_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chain TEXT NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    current_price REAL,
    volume REAL,
    price_change_percentage_24h REAL,
    market_cap REAL,
    UNIQUE(chain, timestamp)
);

CREATE TABLE IF NOT EXISTS mood_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chain TEXT NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    mood TEXT NOT NULL,
    UNIQUE(chain, timestamp)
);

CREATE TABLE IF NOT EXISTS correlation_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    price_correlation REAL,
    volume_correlation REAL,
    market_cap_ratio REAL
);" > schema_modifications.sql
    sqlite3 data/crypto_history.db < schema_modifications.sql
fi

# Create dashboard files
log_info "Creating dashboard files..."

# Creating dashboard.py
if [ ! -f "dashboard.py" ]; then
    log_info "Creating dashboard.py..."
    # Copy dashboard.py content here
    cat > dashboard.py << 'EOL'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# dashboard.py - Real-time crypto analysis dashboard
import os
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
import threading
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create a database connection using your existing configuration
try:
    from config import config
    db = config.db
except ImportError:
    # Fallback if config import fails
    import sqlite3
    db_path = os.getenv('DATABASE_PATH', 'data/crypto_history.db')
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    db = conn

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('DASHBOARD_SECRET_KEY', 'default_secret_key')
socketio = SocketIO(app, cors_allowed_origins="*")

# Data cache
cache = {
    'price_history': {
        'SOL': [],
        'DOT': []
    },
    'volume_history': {
        'SOL': [],
        'DOT': []
    },
    'correlations': [],
    'moods': {
        'SOL': [],
        'DOT': []
    },
    'latest_analysis': ''
}

# Helper functions
def get_price_history(chain, time_cutoff):
    """Get price history for a specific chain since the given cutoff time"""
    query = """
        SELECT timestamp, current_price as price
        FROM market_data
        WHERE chain = ? AND timestamp >= ?
        ORDER BY timestamp ASC
    """
    try:
        cursor = db.cursor() if hasattr(db, 'cursor') else db.conn.cursor()
        cursor.execute(query, (chain, time_cutoff.isoformat()))
        rows = cursor.fetchall()
        return [{'timestamp': row[0], 'price': row[1]} for row in rows]
    except Exception as e:
        print(f"Error getting price history: {e}")
        return []

def get_volume_history(chain, time_cutoff):
    """Get volume history for a specific chain since the given cutoff time"""
    query = """
        SELECT timestamp, volume
        FROM market_data
        WHERE chain = ? AND timestamp >= ?
        ORDER BY timestamp ASC
    """
    try:
        cursor = db.cursor() if hasattr(db, 'cursor') else db.conn.cursor()
        cursor.execute(query, (chain, time_cutoff.isoformat()))
        rows = cursor.fetchall()
        return [{'timestamp': row[0], 'volume': row[1]} for row in rows]
    except Exception as e:
        print(f"Error getting volume history: {e}")
        return []

def get_mood_history(chain, time_cutoff):
    """Get mood history for a specific chain since the given cutoff time"""
    query = """
        SELECT timestamp, mood
        FROM mood_data
        WHERE chain = ? AND timestamp >= ?
        ORDER BY timestamp ASC
    """
    try:
        cursor = db.cursor() if hasattr(db, 'cursor') else db.conn.cursor()
        cursor.execute(query, (chain, time_cutoff.isoformat()))
        rows = cursor.fetchall()
        return [{'timestamp': row[0], 'mood': row[1]} for row in rows]
    except Exception as e:
        print(f"Error getting mood history: {e}")
        return []

def get_correlation_history(time_cutoff):
    """Get correlation history since the given cutoff time"""
    query = """
        SELECT timestamp, price_correlation, volume_correlation, market_cap_ratio
        FROM correlation_data
        WHERE timestamp >= ?
        ORDER BY timestamp ASC
    """
    try:
        cursor = db.cursor() if hasattr(db, 'cursor') else db.conn.cursor()
        cursor.execute(query, (time_cutoff.isoformat(),))
        rows = cursor.fetchall()
        return [{
            'timestamp': row[0],
            'price_correlation': row[1],
            'volume_correlation': row[2],
            'market_cap_ratio': row[3]
        } for row in rows]
    except Exception as e:
        print(f"Error getting correlation history: {e}")
        return []

def get_latest_post():
    """Get the most recent posted analysis"""
    query = """
        SELECT timestamp, content, trigger_type
        FROM posted_content
        ORDER BY timestamp DESC
        LIMIT 1
    """
    try:
        cursor = db.cursor() if hasattr(db, 'cursor') else db.conn.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
        if row:
            return {
                'timestamp': row[0],
                'content': row[1],
                'trigger_type': row[2]
            }
        return None
    except Exception as e:
        print(f"Error getting latest post: {e}")
        return None

# Routes
@app.route('/')
def index():
    """Serve the main dashboard page"""
    return render_template('index.html')

@app.route('/api/current-data')
def get_current_data():
    """API endpoint to get current market data"""
    return jsonify(cache)

# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"Client connected: {datetime.now()}")
    # Send initial data to client
    socketio.emit('initial_data', cache)

def update_cache():
    """Update the data cache from database"""
    # Get the last 24 hours of price data
    time_cutoff = datetime.now() - timedelta(hours=24)
    
    # Fetch price history
    for chain in ['SOL', 'DOT']:
        prices = get_price_history(chain, time_cutoff)
        cache['price_history'][chain] = [
            {'timestamp': row['timestamp'], 'price': row['price']} 
            for row in prices
        ]
        
        # Fetch volume history
        volumes = get_volume_history(chain, time_cutoff)
        cache['volume_history'][chain] = [
            {'timestamp': row['timestamp'], 'volume': row['volume']} 
            for row in volumes
        ]
        
        # Fetch mood history
        moods = get_mood_history(chain, time_cutoff)
        cache['moods'][chain] = [
            {'timestamp': row['timestamp'], 'mood': row['mood']} 
            for row in moods
        ]
    
    # Fetch correlation history
    correlations = get_correlation_history(time_cutoff)
    cache['correlations'] = [
        {
            'timestamp': row['timestamp'],
            'price_correlation': row['price_correlation'],
            'volume_correlation': row['volume_correlation'],
            'market_cap_ratio': row['market_cap_ratio']
        }
        for row in correlations
    ]
    
    # Fetch latest analysis
    latest_post = get_latest_post()
    if latest_post:
        cache['latest_analysis'] = latest_post['content']
    
    # Emit updated data to connected clients
    socketio.emit('data_update', cache)

def background_thread():
    """Background thread that updates cache and emits to clients"""
    while True:
        update_cache()
        time.sleep(30)  # Update every 30 seconds

# Start background thread for updates
def start_background_thread():
    thread = threading.Thread(target=background_thread)
    thread.daemon = True
    thread.start()

@app.before_first_request
def before_first_request():
    """Start the background thread before first request"""
    start_background_thread()

if __name__ == '__main__':
    # Ensure the templates directory exists
    os.makedirs('templates', exist_ok=True)
    
    # Update cache once at startup
    update_cache()
    
    # Start the backgroun
