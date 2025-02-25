# Layer 1 Crypto Analysis Dashboard

A real-time visualization dashboard for Layer 1 blockchain analytics, designed to work with the Layer1AnalysisBot.

![Dashboard Preview](https://via.placeholder.com/1200x600?text=Layer+1+Crypto+Analysis+Dashboard)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Quick Start](#quick-start)
- [Installation](#installation)
  - [Automated Installation](#automated-installation)
  - [Manual Installation](#manual-installation)
- [Configuration](#configuration)
- [Dashboard Components](#dashboard-components)
- [Data Integration](#data-integration)
- [Deployment](#deployment)
  - [Local Development](#local-development)
  - [Production Server](#production-server)
  - [Docker Deployment](#docker-deployment)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)
- [Architecture](#architecture)
- [Database Schema](#database-schema)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [License](#license)

## 🔍 Overview

The Layer 1 Crypto Analysis Dashboard provides a visual interface for analyzing cryptocurrency market data, specifically designed for Solana (SOL) and Polkadot (DOT). It connects to your existing Layer1AnalysisBot, which collects and processes market data, and presents this information through interactive charts and indicators.

This dashboard enables real-time monitoring of:
- Price movements
- Trading volume
- Cross-chain correlations
- Market sentiment (mood)
- Latest market analysis

## ✨ Features

- **Real-time Updates**: Uses WebSockets to provide instant data visualization without page refreshes
- **Interactive Charts**: Visualizes price and volume data with zooming and tooltips
- **Correlation Analysis**: Shows the relationship between different Layer 1 blockchains
- **Sentiment Indicators**: Visual representation of market mood (bullish, bearish, neutral)
- **Latest Analysis**: Displays the most recent market analysis from your bot
- **Responsive Design**: Works on desktop and mobile devices
- **Dark/Light Mode**: Toggle between viewing preferences
- **Multiple Deployment Options**: Run locally, on a web server, or with Docker

## 📋 Requirements

- Python 3.7+
- SQLite database
- Your existing Layer1AnalysisBot setup
- Web server (for production deployment)

## 🚀 Quick Start

For the fastest setup, use the automated installation script:

```bash
# Download the installation script
curl -O https://raw.githubusercontent.com/yourusername/crypto-dashboard/main/install_dashboard.sh

# Make it executable
chmod +x install_dashboard.sh

# Run the installer
./install_dashboard.sh

# Start the dashboard
./start_dashboard.sh
```

Then open your browser to `http://localhost:5000`

## 📦 Installation

### Automated Installation

The easiest way to install is using the provided installation script:

```bash
./install_dashboard.sh
```

This script will:
1. Check your environment for prerequisites
2. Install required Python packages
3. Set up the necessary database tables
4. Create the dashboard application files
5. Configure environment variables
6. Create a startup script

### Manual Installation

If you prefer to install manually, follow these steps:

1. **Prepare your environment**:
   ```bash
   # Create necessary directories
   mkdir -p templates static data
   ```

2. **Install dependencies**:
   ```bash
   pip install flask flask-socketio eventlet python-dotenv requests gunicorn
   ```

3. **Set up the database**:
   ```bash
   # Apply schema modifications to your existing database
   sqlite3 data/crypto_history.db < schema_modifications.sql
   ```

4. **Create dashboard files**:
   - Create `dashboard.py` with the code from the dashboard architecture
   - Create `templates/index.html` with the dashboard template
   - Add the database helper methods to your existing `database.py`

5. **Configure environment variables**:
   ```bash
   cp env-template.txt .env
   # Edit .env with your specific settings
   ```

6. **Start the dashboard**:
   ```bash
   python dashboard.py
   ```

## ⚙️ Configuration

Configuration is managed through environment variables in the `.env` file:

```
# API Keys
CLAUDE_API_KEY=your_claude_api_key_here
COINGECKO_API_KEY=your_coingecko_api_key_here  # Optional

# Dashboard Config
DASHBOARD_SECRET_KEY=your_secret_key_here
DATABASE_PATH=data/crypto_history.db

# Optional: Analytics
ENABLE_ANALYTICS=false
GOOGLE_ANALYTICS_ID=your_analytics_id
```

## 📊 Dashboard Components

The dashboard consists of several visualization components:

### 1. Market Overview Panel
- Current price and 24h change for SOL and DOT
- Market mood indicators
- Last updated timestamp
- Latest market analysis text

### 2. Price Charts
- 24-hour price history for SOL and DOT
- Interactive timeline with zooming capability
- Price tooltips on hover

### 3. Volume Charts
- 24-hour trading volume for SOL and DOT
- Bar chart representation
- Volume tooltips on hover

### 4. Correlation Analysis
- Price correlation gauge
- Volume correlation gauge
- Market cap ratio chart

## 📝 Data Integration

To integrate the dashboard with your Layer1AnalysisBot, follow these steps:

1. **Add database methods**: Add the provided helper methods to your `database.py` file.

2. **Update your bot**: Ensure your bot is saving all required data:
   - Market data (price, volume, etc.)
   - Mood/sentiment data
   - Correlation analysis
   - Posted content

3. **Verify data storage**: Check that your database tables are being populated correctly.

For detailed integration instructions, see the [Data Integration Guide](data-integration-guide.md).

## 🌐 Deployment

### Local Development

For local development and testing:

```bash
python dashboard.py
```

This will start the Flask development server at `http://localhost:5000`.

### Production Server

For production deployment:

1. **Set up Nginx**:
   ```bash
   sudo cp nginx-crypto-dashboard.conf /etc/nginx/sites-available/
   sudo ln -s /etc/nginx/sites-available/nginx-crypto-dashboard.conf /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

2. **Configure systemd service**:
   ```bash
   sudo cp crypto-dashboard.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable crypto-dashboard
   sudo systemctl start crypto-dashboard
   ```

3. **Set up SSL certificates**:
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

### Docker Deployment

For containerized deployment:

```bash
# Build and start containers
docker-compose up -d

# View logs
docker-compose logs -f

# Update application
docker-compose down
git pull
docker-compose up --build -d
```

## 🎨 Customization

### Adding New Charts

To add a new chart:

1. **Add HTML elements** to `index.html`:
   ```html
   <div class="chart-container">
       <canvas id="new-chart"></canvas>
   </div>
   ```

2. **Add JavaScript** to initialize and update the new chart:
   ```javascript
   // Initialize chart
   newChart = new Chart(document.getElementById('new-chart').getContext('2d'), {
       // Chart configuration
   });
   
   // Update function
   function updateCharts(data) {
       // Existing code
       
       // Update new chart
       const newData = data.new_data.map(item => ({
           x: new Date(item.timestamp),
           y: item.value
       }));
       newChart.data.datasets[0].data = newData;
       newChart.update();
   }
   ```

3. **Add backend support** in `dashboard.py`:
   ```python
   # Add to cache
   cache['new_data'] = []
   
   # Add to update_cache function
   def update_cache():
       # Existing code
       
       # Fetch new data
       new_data = get_new_data()
       cache['new_data'] = new_data
   ```

### Styling Modifications

The dashboard uses Tailwind CSS for styling. To modify the appearance:

1. **Modify color scheme**:
   ```html
   <!-- Change the color classes in the HTML -->
   <div class="bg-blue-500 text-white">...</div>
   ```

2. **Change the layout**:
   ```html
   <!-- Adjust grid layout -->
   <div class="grid grid-cols-1 md:grid-cols-3 gap-4">...</div>
   ```

## 🔧 Troubleshooting

### Common Issues

#### No Data Displayed

- Check that the bot is running and storing data
- Verify database permissions and file paths
- Check database tables for data

```bash
sqlite3 data/crypto_history.db
sqlite> SELECT count(*) FROM market_data;
sqlite> SELECT count(*) FROM mood_data;
sqlite> SELECT count(*) FROM correlation_data;
```

#### WebSocket Connection Failures

- Ensure your firewall allows WebSocket connections
- Check for any proxy interference
- Verify Nginx WebSocket configuration

#### Dashboard Won't Start

- Check for port conflicts
- Ensure all dependencies are installed
- Verify Python version compatibility

## 🏗️ Architecture

The dashboard follows a modular architecture:

1. **Data Collection Layer**: Your existing Layer1AnalysisBot collects and stores data
2. **Database Layer**: SQLite database stores historical data
3. **API Layer**: Flask backend provides data access endpoints
4. **Real-time Communication Layer**: WebSockets handle real-time updates
5. **Presentation Layer**: HTML/CSS/JS frontend visualizes the data

### Data Flow

```
Bot → Database → Flask Backend → WebSockets → Browser Frontend
```

## 💾 Database Schema

The dashboard uses the following database tables:

### market_data
```sql
CREATE TABLE market_data (
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
```

### mood_data
```sql
CREATE TABLE mood_data (
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
```

### correlation_data
```sql
CREATE TABLE correlation_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    price_correlation REAL,
    volume_correlation REAL,
    market_cap_ratio REAL
);
```

### posted_content
```sql
CREATE TABLE posted_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    content TEXT NOT NULL,
    sentiment TEXT,
    trigger_type TEXT,
    price_data TEXT,
    meme_phrases TEXT
);
```

## 📚 API Reference

The dashboard provides the following API endpoints:

### Main Dashboard UI
- `GET /` - Renders the main dashboard interface

### Data API
- `GET /api/current-data` - Returns all current dashboard data as JSON

### WebSocket Events
- `connect` - Client connection event
- `initial_data` - Sends initial data on connection
- `data_update` - Sends data updates to clients

## 👨‍💻 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📬 Contact

For questions or support, please open an issue on the GitHub repository.

---

*Dashboard powered by Flask, Socket.IO, and Chart.js*
