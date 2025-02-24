#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# dashboard.py - Real-time crypto analysis dashboard for Layer1AnalysisBot
import os
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
import threading
import time
from database import CryptoDatabase
from config import config

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Database connection (reusing the existing database)
db = config.db

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
        prices = db.get_price_history(chain, time_cutoff)
        cache['price_history'][chain] = [
            {'timestamp': row['timestamp'], 'price': row['price']} 
            for row in prices
        ]
        
        # Fetch volume history
        volumes = db.get_volume_history(chain, time_cutoff)
        cache['volume_history'][chain] = [
            {'timestamp': row['timestamp'], 'volume': row['volume']} 
            for row in volumes
        ]
        
        # Fetch mood history
        moods = db.get_mood_history(chain, time_cutoff)
        cache['moods'][chain] = [
            {'timestamp': row['timestamp'], 'mood': row['mood']} 
            for row in moods
        ]
    
    # Fetch correlation history
    correlations = db.get_correlation_history(time_cutoff)
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
    latest_post = db.get_latest_post()
    if latest_post:
        cache['latest_analysis'] = latest_post['content']
    
    # Emit updated data to connected clients
    socketio.emit('data_update', cache)

def background_thread():
    """Background thread that updates cache and emits to clients"""
    while True:
        update_cache()
        time.sleep(30)  # Update every 30 seconds

@app.before_first_request
def start_background_thread():
    """Start the background thread before first request"""
    thread = threading.Thread(target=background_thread)
    thread.daemon = True
    thread.start()

if __name__ == '__main__':
    # Ensure the templates directory exists
    os.makedirs('templates', exist_ok=True)
    
    # Update cache once at startup
    update_cache()
    
    # Start the Socket.IO server
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
