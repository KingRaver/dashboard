# Layer 1 Crypto Analysis Dashboard: Complete Installation Guide

This comprehensive guide will walk you through setting up the real-time crypto analysis dashboard for your Layer1AnalysisBot.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Preparation](#preparation)
3. [Database Setup](#database-setup)
4. [Dashboard Installation](#dashboard-installation)
5. [Running Locally](#running-locally)
6. [Production Deployment](#production-deployment)
   - [Standard Server Deployment](#standard-server-deployment)
   - [Docker Deployment](#docker-deployment)
7. [Troubleshooting](#troubleshooting)
8. [Customization](#customization)

## Prerequisites

Before beginning installation, ensure you have:

- Python 3.7+ installed
- Your Layer1AnalysisBot code working properly
- Access to a web server for production deployment (optional)
- Basic understanding of the command line

## Preparation

1. **Organize your project structure**:
   ```
   project_directory/
   ├── bot.py                 # Your existing Layer1AnalysisBot
   ├── coingecko_handler.py   # Your existing handler
   ├── config.py              # Your configuration file
   ├── database.py            # Your database module
   ├── data/                  # Directory for database files
   │   └── crypto_history.db  # Your SQLite database
   └── utils/                 # Utilities folder
   ```

2. **Create environment file**:
   - Copy the provided `.env.template` to `.env`
   - Fill in your API keys and other sensitive information
   ```bash
   cp .env.template .env
   nano .env  # Edit with your values
   ```

3. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Database Setup

1. **Check your existing database**:
   Examine your current database schema to ensure compatibility with the dashboard.

2. **Apply schema modifications**:
   Run the provided SQL script to add any missing tables needed for the dashboard:
   ```bash
   sqlite3 data/crypto_history.db < schema_modifications.sql
   ```

3. **Verify the database structure**:
   ```bash
   sqlite3 data/crypto_history.db
   .tables
   .schema market_data
   .schema mood_data
   .schema correlation_data
   .quit
   ```

## Dashboard Installation

1. **Create dashboard files**:
   - Create a new file `dashboard.py` with the provided code
   - Create a `templates` directory
   - Create `templates/index.html` with the provided template

2. **Add database methods**:
   Add the provided helper methods to your existing `database.py` file.

3. **Test the imports**:
   ```bash
   python -c "from dashboard import app; print('Dashboard imports successful')"
   ```

## Running Locally

1. **Start the dashboard application**:
   ```bash
   python dashboard.py
   ```

2. **Access the dashboard**:
   Open your web browser and navigate to `http://localhost:5000`

3. **Run your bot separately**:
   ```bash
   python bot.py
   ```

## Production Deployment

### Standard Server Deployment

1. **Set up a systemd service**:
   - Copy the provided `crypto-dashboard.service` to `/etc/systemd/system/`
   - Edit the file to match your environment
   - Enable and start the service:
   ```bash
   sudo cp crypto-dashboard.service /etc/systemd/system/
   sudo nano /etc/systemd/system/crypto-dashboard.service  # Edit paths
   sudo systemctl daemon-reload
   sudo systemctl enable crypto-dashboard
   sudo systemctl start crypto-dashboard
   ```

2. **Configure Nginx**:
   - Copy the provided Nginx configuration to `/etc/nginx/sites-available/`
   - Create a symlink to sites-enabled
   - Test and restart Nginx
   ```bash
   sudo cp nginx-crypto-dashboard.conf /etc/nginx/sites-available/
   sudo ln -s /etc/nginx/sites-available/nginx-crypto-dashboard.conf /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

3. **Set up SSL certificates**:
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

### Docker Deployment

1. **Build and run with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

2. **Check logs**:
   ```bash
   docker-compose logs -f
   ```

3. **Update the application**:
   ```bash
   git pull  # Get latest changes
   docker-compose build  # Rebuild containers
   docker-compose up -d  # Restart containers
   ```

## Troubleshooting

### Common Issues:

1. **Dashboard shows no data**:
   - Check that your bot is running and storing data in the database
   - Verify database permissions and file paths
   - Check the dashboard logs for errors:
   ```bash
   sudo journalctl -u crypto-dashboard
   ```

2. **WebSocket connection failures**:
   - Ensure your firewall allows WebSocket connections
   - Check Nginx configuration for WebSocket proxy settings
   - Test direct connection to port 5000

3. **Database errors**:
   - Check SQL syntax in your custom queries
   - Verify the database file exists and is readable
   - Check for disk space issues

## Customization

### Styling the Dashboard:

1. **Modify the HTML template**:
   - Edit `templates/index.html` to change layout and styling
   - The template uses Tailwind CSS, so you can use utility classes

2. **Add custom charts**:
   - Edit the JavaScript in the HTML template to add or modify charts
   - Add corresponding methods to fetch data in `dashboard.py`

3. **Add authentication**:
   - Implement Flask-Login for basic authentication
   - Or add a simple username/password prompt
