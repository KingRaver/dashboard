# Crypto Analysis Dashboard Deployment Guide

This guide will help you deploy the real-time crypto analysis dashboard for your Layer1AnalysisBot.

## Prerequisites

- Python 3.7+
- Your existing crypto automation setup
- Web server (for production deployment)

## Installation Steps

### 1. Install Required Packages

```bash
pip install flask flask-socketio eventlet
```

### 2. Add Database Helper Methods

Add the provided database helper methods to your existing `CryptoDatabase` class in `database.py`. These methods will allow the dashboard to query historical data.

### 3. Create Directory Structure

Create the following structure:

```
your_project_directory/
├── dashboard.py           # Main dashboard application
├── templates/             # HTML templates
│   └── index.html         # Dashboard template
├── static/                # Static assets (if needed)
├── config.py              # Your existing config file
├── database.py            # Your existing database file with added methods
└── other existing files...
```

### 4. Set Up the Dashboard Files

1. Create the `dashboard.py` file using the provided code
2. Create the `templates` directory and add the `index.html` file

### 5. Test Locally

Run the dashboard application:

```bash
python dashboard.py
```

Then open a web browser and navigate to `http://localhost:5000` to view your dashboard.

## Running the Dashboard with Your Bot

### Option 1: Run as Separate Process

You can run the dashboard as a separate process alongside your existing bot:

```bash
# Terminal 1 - Run your bot
python bot.py

# Terminal 2 - Run the dashboard
python dashboard.py
```

### Option 2: Integrate with Your Bot (Advanced)

You can integrate the dashboard directly into your bot by adding the Flask app to your bot's main file and running it in a separate thread:

```python
# In your Layer1AnalysisBot class
def start(self) -> None:
    # Start the dashboard in a separate thread
    dashboard_thread = threading.Thread(target=self._run_dashboard)
    dashboard_thread.daemon = True
    dashboard_thread.start()
    
    # Original bot execution continues...
    try:
        # Existing bot code...
    except KeyboardInterrupt:
        # Existing shutdown code...
        
def _run_dashboard(self):
    """Run the Flask dashboard application"""
    from dashboard import app, socketio
    socketio.run(app, debug=False, host='0.0.0.0', port=5000)
```

## Production Deployment

For production deployment, consider the following options:

### Using Gunicorn with Eventlet

```bash
pip install gunicorn eventlet
gunicorn --worker-class eventlet -w 1 dashboard:app
```

### Nginx Reverse Proxy

For better performance and security, use Nginx as a reverse proxy:

1. Install Nginx
2. Configure Nginx to forward requests to your dashboard application
3. Set up SSL certificates for secure HTTPS connections

Example Nginx configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Customization

### Styling

The dashboard template uses Tailwind CSS for styling. You can customize the look and feel by modifying the HTML template.

### Additional Charts

To add more visualizations, you can:

1. Add HTML elements in the template
2. Update the JavaScript code to initialize and update new charts
3. Add corresponding data endpoints in the Flask application

## Troubleshooting

### Common Issues

1. **Database connection errors**: Make sure the dashboard has access to the same database file as your bot.
2. **WebSocket connection issues**: Check for firewall or proxy settings that might block WebSocket connections.
3. **Missing data**: Verify that your bot is correctly storing data in the database tables.

### Debug Mode

For troubleshooting, run the dashboard in debug mode:

```bash
python dashboard.py --debug
```

This will provide detailed error messages in the browser console.
