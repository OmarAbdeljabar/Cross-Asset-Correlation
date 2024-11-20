import pandas as pd
import yfinance as yf
from datetime import datetime

def update_btc_data():
    # Load existing data
    print("Loading existing market data...")
    existing_data = pd.read_parquet('market_prices_stooq.parquet')
    start_date = existing_data.index.min()
    end_date = existing_data.index.max()
    
    print(f"Fetching BTC data from {start_date.date()} to {end_date.date()}")
    
    # Fetch BTC-USD from Yahoo Finance
    btc = yf.download('BTC-USD', 
                      start=start_date,
                      end=end_date,
                      progress=False)
    
    # Align BTC data with existing dates
    btc_closes = btc['Close'].reindex(existing_data.index)
    
    # Update BTC column
    existing_data['BTC'] = btc_closes
    
    # Save updated data
    existing_data.to_parquet('market_prices_stooq.parquet', compression='snappy')
    
    print("\nBTC Data Statistics:")
    print(f"First date: {existing_data['BTC'].first_valid_index().date()}")
    print(f"Last date: {existing_data['BTC'].last_valid_index().date()}")
    print(f"Number of valid BTC prices: {existing_data['BTC'].count()}")
    print(f"Number of missing values: {existing_data['BTC'].isna().sum()}")
    
    return existing_data

if __name__ == "__main__":
    try:
        updated_data = update_btc_data()
    except Exception as e:
        print(f"Error: {e}")