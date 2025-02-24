# Data Integration Guide for Layer 1 Analysis Dashboard

This guide explains how to integrate data collection for the dashboard into your existing Layer1AnalysisBot code. By making a few strategic additions to your bot, you can ensure all the necessary data is properly stored for visualization.

## Table of Contents
1. [Understanding Data Requirements](#understanding-data-requirements)
2. [Database Integration](#database-integration)
3. [Modifying the CoinGeckoHandler](#modifying-the-coingeckohandler)
4. [Updating the Layer1AnalysisBot](#updating-the-layer1analysisbot)
5. [Testing Data Collection](#testing-data-collection)

## Understanding Data Requirements

The dashboard requires the following data points:

1. **Price & Volume Data**: Historical price and trading volume for SOL and DOT
2. **Mood Data**: The market sentiment (bullish/bearish/neutral) for each chain
3. **Correlation Data**: Correlation metrics between SOL and DOT
4. **Analysis Content**: The latest market analysis text

## Database Integration

Your bot already stores much of this data. We need to ensure all required data is being saved in the format the dashboard expects.

### 1. Add database methods to `database.py`:

```python
# Add these methods to your CryptoDatabase class

def store_market_data(self, chain, data):
    """Store market data for a specific chain"""
    query = """
        INSERT OR REPLACE INTO market_data 
        (chain, timestamp, current_price, volume, price_change_percentage_24h, 
         market_cap, market_cap_rank, total_supply, max_supply, circulating_supply,
         ath, ath_change_percentage)
        VALUES (?, datetime('now'), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    try:
        self.cursor.execute(query, (
            chain,
            data.get('current_price'),
            data.get('volume'),
            data.get('price_change_percentage_24h'),
            data.get('market_cap'),
            data.get('market_cap_rank'),
            data.get('total_supply'),
            data.get('max_supply'),
            data.get('circulating_supply'),
            data.get('ath'),
            data.get('ath_change_percentage')
        ))
        self.conn.commit()
    except Exception as e:
        print(f"Error storing market data: {e}")

def store_mood(self, chain, mood, indicators=None):
    """Store mood data for a specific chain"""
    query = """
        INSERT INTO mood_data 
        (chain, timestamp, mood, price_change, trading_volume, volatility,
         social_sentiment, funding_rates, liquidation_volume)
        VALUES (?, datetime('now'), ?, ?, ?, ?, ?, ?, ?)
    """
    try:
        if indicators:
            self.cursor.execute(query, (
                chain,
                mood,
                indicators.price_change,
                indicators.trading_volume,
                indicators.volatility,
                indicators.social_sentiment,
                indicators.funding_rates,
                indicators.liquidation_volume
            ))
        else:
            self.cursor.execute(query, (
                chain,
                mood,
                None, None, None, None, None, None
            ))
        self.conn.commit()
    except Exception as e:
        print(f"Error storing mood data: {e}")

def store_correlation_analysis(self, correlations):
    """Store correlation analysis data"""
    query = """
        INSERT INTO correlation_data 
        (timestamp, price_correlation, volume_correlation, market_cap_ratio)
        VALUES (datetime('now'), ?, ?, ?)
    """
    try:
        self.cursor.execute(query, (
            correlations.get('price_correlation'),
            correlations.get('volume_correlation'),
            correlations.get('market_cap_ratio')
        ))
        self.conn.commit()
    except Exception as e:
        print(f"Error storing correlation data: {e}")

def store_posted_content(self, content, sentiment=None, trigger_type=None, price_data=None, meme_phrases=None):
    """Store posted content with metadata"""
    query = """
        INSERT INTO posted_content 
        (timestamp, content, sentiment, trigger_type, price_data, meme_phrases)
        VALUES (datetime('now'), ?, ?, ?, ?, ?)
    """
    try:
        import json
        sentiment_json = json.dumps(sentiment) if sentiment else None
        price_data_json = json.dumps(price_data) if price_data else None
        meme_phrases_json = json.dumps(meme_phrases) if meme_phrases else None
        
        self.cursor.execute(query, (
            content,
            sentiment_json,
            trigger_type,
            price_data_json,
            meme_phrases_json
        ))
        self.conn.commit()
    except Exception as e:
        print(f"Error storing posted content: {e}")

def get_chain_stats(self, chain, hours=24):
    """Get statistics for a chain over the specified time period"""
    query = """
        SELECT 
            AVG(current_price) as avg_price,
            MAX(current_price) as max_price,
            MIN(current_price) as min_price,
            AVG(volume) as avg_volume,
            MAX(volume) as max_volume,
            COUNT(*) as data_points
        FROM market_data
        WHERE chain = ? AND timestamp >= datetime('now', ?)
    """
    try:
        self.cursor.execute(query, (chain, f'-{hours} hours'))
        row = self.cursor.fetchone()
        if row and row[0]:  # Check if we have valid data
            return {
                'avg_price': row[0],
                'max_price': row[1],
                'min_price': row[2],
                'avg_volume': row[3],
                'max_volume': row[4],
                'data_points': row[5]
            }
        return None
    except Exception as e:
        print(f"Error getting chain stats: {e}")
        return None

def check_content_similarity(self, content, threshold=0.8):
    """Check if similar content was recently posted"""
    query = """
        SELECT content FROM posted_content 
        WHERE timestamp >= datetime('now', '-1 day')
        ORDER BY timestamp DESC
        LIMIT 10
    """
    try:
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        
        for row in rows:
            existing_content = row[0]
            # Simple similarity check - can be improved
            if existing_content and content:
                similarity = self._calculate_similarity(existing_content, content)
                if similarity > threshold:
                    return True
        return False
    except Exception as e:
        print(f"Error checking content similarity: {e}")
        return False
        
def _calculate_similarity(self, text1, text2):
    """Simple text similarity calculation"""
    # Convert to sets of words for comparison
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    # Calculate Jaccard similarity
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    if union == 0:
        return 0
    return intersection / union
```

## Modifying the CoinGeckoHandler

Your `CoinGeckoHandler` class already has most of the functionality needed. Just ensure that it fetches all required data fields:

```python
# In your coingecko_handler.py file, ensure the market data response includes:
# - current_price
# - price_change_percentage_24h
# - total_volume
# - market_cap
# - market_cap_rank
# - ath (all-time high)
# - ath_change_percentage

# Example modification to the get_market_data method:
def get_market_data(self, params, max_retries=3):
    # Ensure these fields are included in the response
    params['vs_currency'] = params.get('vs_currency', 'usd')
    params['price_change_percentage'] = params.get('price_change_percentage', '24h')
    params['sparkline'] = params.get('sparkline', True)
    
    # Rest of your existing method...
```

## Updating the Layer1AnalysisBot

Now we need to ensure your bot is saving all required data during its normal operation.

### 1. Update the `_get_crypto_data` method:

```python
def _get_crypto_data(self) -> Optional[Dict[str, Any]]:
    """Fetch SOL and DOT data from CoinGecko with retries"""
    try:
        params = {
            **self.config.get_coingecko_params(),
            'ids': ','.join(self.target_chains.values()), 
            'sparkline': True,
            'price_change_percentage': '1h,24h,7d'  # Ensure we get price change data
        }
        
        data = self.coingecko.get_market_data(params)
        if not data:
            logger.logger.error("Failed to fetch market data from CoinGecko")
            return None
            
        formatted_data = {
            coin['symbol'].upper(): {
                'current_price': coin['current_price'],
                'volume': coin['total_volume'],
                'price_change_percentage_24h': coin['price_change_percentage_24h'],
                'sparkline': coin.get('sparkline_in_7d', {}).get('price', []),
                'market_cap': coin['market_cap'],
                'market_cap_rank': coin['market_cap_rank'],
                'total_supply': coin.get('total_supply'),
                'max_supply': coin.get('max_supply'),
                'circulating_supply': coin.get('circulating_supply'),
                'ath': coin.get('ath'),
                'ath_change_percentage': coin.get('ath_change_percentage')
            } for coin in data
        }
        
        # Store market data in database
        for chain, chain_data in formatted_data.items():
            self.config.db.store_market_data(chain, chain_data)
        
        return formatted_data
                
    except Exception as e:
        logger.log_error("CoinGecko API", str(e))
        return None
```

### 2. Verify the `_calculate_correlations` method:

```python
def _calculate_correlations(self, market_data: Dict[str, Any]) -> Dict[str, float]:
    """Calculate L1 correlations and patterns"""
    try:
        sol_data = market_data['SOL']
        dot_data = market_data['DOT']
        
        price_correlation = abs(
            sol_data['price_change_percentage_24h'] - 
            dot_data['price_change_percentage_24h']
        ) / max(abs(sol_data['price_change_percentage_24h']), 
               abs(dot_data['price_change_percentage_24h']))
        
        volume_correlation = abs(
            (sol_data['volume'] - dot_data['volume']) / 
            max(sol_data['volume'], dot_data['volume'])
        )
        
        market_cap_ratio = sol_data['market_cap'] / dot_data['market_cap']
        
        correlations = {
            'price_correlation': 1 - price_correlation,
            'volume_correlation': 1 - volume_correlation,
            'market_cap_ratio': market_cap_ratio
        }
        
        # Store correlation data
        self.config.db.store_correlation_analysis(correlations)
        
        return correlations
            
    except Exception as e:
        logger.log_error("Correlation Calculation", str(e))
        return {
            'price_correlation': 0.0,
            'volume_correlation': 0.0,
            'market_cap_ratio': 1.0
        }
```

### 3. Ensure mood data is stored:

```python
# In the _analyze_market_sentiment method, ensure this section properly stores mood data:

for chain, data in crypto_data.items():
    indicators = MoodIndicators(
        price_change=data['price_change_percentage_24h'],
        trading_volume=data['volume'],
        volatility=abs(data['price_change_percentage_24h']) / 100,
        social_sentiment=None,
        funding_rates=None,
        liquidation_volume=None
    )
    
    mood = determine_advanced_mood(indicators)
    chain_moods[chain] = {
        'mood': mood.value,
        'change': data['price_change_percentage_24h'],
        'ath_distance': data['ath_change_percentage']
    }
    
    # Store mood data
    self.config.db.store_mood(chain, mood.value, indicators)
```

### 4. Make sure Twitter posts are saved to the database:

```python
# In the _post_analysis method, add:

def _post_analysis(self, tweet_text: str) -> bool:
    """Post analysis to Twitter with robust button handling"""
    max_retries = 3
    retry_count = 0
    
    # Existing Twitter posting code...
    
    # If posting was successful, store the content
    if posting_success:
        self.config.db.store_posted_content(
            content=tweet_text,
            sentiment=chain_moods,  # Pass the mood data
            trigger_type=trigger_type,
            price_data={chain: {'price': data['current_price'], 
                              'volume': data['volume']} 
                      for chain, data in crypto_data.items()},
            meme_phrases=meme_context if 'meme_context' in locals() else None
        )
    
    return posting_success
```

## Testing Data Collection

After implementing these changes, you should verify that data is being properly collected:

1. Run your bot for a few analysis cycles
2. Check the database tables to ensure data is being stored correctly:

```bash
sqlite3 data/crypto_history.db

# Check market data table
sqlite> SELECT COUNT(*), chain FROM market_data GROUP BY chain;

# Check mood data table
sqlite> SELECT COUNT(*), chain, mood FROM mood_data GROUP BY chain, mood;

# Check correlation data table
sqlite> SELECT COUNT(*), AVG(price_correlation) FROM correlation_data;

# Check posted content table
sqlite> SELECT COUNT(*), MAX(timestamp) FROM posted_content;

# Exit SQLite
sqlite> .quit
```

3. Start the dashboard and verify that it displays the data correctly

Once the data collection is properly integrated, the dashboard will automatically fetch and display this information.
