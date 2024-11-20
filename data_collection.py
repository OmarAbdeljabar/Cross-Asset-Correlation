import pandas as pd
import pandas_datareader.data as web
from datetime import datetime, timedelta
import time
from multiprocessing import Pool, cpu_count
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Define market tickers by category
MARKET_TICKERS = {
    'Major_Market_ETFs': ['SPY', 'QQQ', 'IWM', 'IJR', 'IJH', 'IWF', 'IWD'],
    'International_Developed': ['EFA', 'EWJ', 'FXI', 'EWG'],
    'Emerging_Markets': ['EEM', 'EWZ', 'INDA', 'EWT', 'EWY', 'EWW'],
    'Fixed_Income': ['TLT', 'IEF', 'LQD', 'HYG', 'BND', 'TIP'],
    'Currencies_Risk': ['UUP', 'FXE'],
    'Sectors': ['XLF', 'XLK', 'XLE', 'XLV', 'XLI', 'XLP', 'XLY', 'XLB', 'XLC', 'XLU'],
    'Real_Estate': ['VNQ'],
    'Commodities': ['GLD', 'SLV', 'USO', 'UNG', 'DBC']
}

def format_ticker(ticker, market='US'):
    return f"{ticker}.{market}"

def fetch_ticker_data(ticker):
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=5*365)
            
            stooq_ticker = format_ticker(ticker)
            df = web.DataReader(stooq_ticker, 'stooq', start_date, end_date)
            
            if not df.empty and 'Close' in df.columns:
                print(f"Successfully fetched {ticker}")
                return ticker, df['Close']
            else:
                print(f"Attempt {attempt}: No data found for {ticker}.")
        except Exception as e:
            print(f"Attempt {attempt} failed for {ticker}: {e}")
        
        time.sleep(2 ** attempt)
    
    print(f"All attempts failed for {ticker}")
    return ticker, None

def main():
    all_tickers = [ticker for sublist in MARKET_TICKERS.values() for ticker in sublist]
    
    # Use only 4 cores to be conservative
    n_cores = min(4, cpu_count())
    print(f"Using {n_cores} cores")
    
    # Process in smaller batches
    batch_size = 10
    valid_data = {}
    
    for i in range(0, len(all_tickers), batch_size):
        batch = all_tickers[i:i+batch_size]
        print(f"\nProcessing batch {i//batch_size + 1} of {(len(all_tickers) + batch_size - 1)//batch_size}")
        
        with Pool(processes=n_cores) as pool:
            results = pool.map(fetch_ticker_data, batch)
        
        # Add valid results to our data dictionary
        batch_data = {ticker: data for ticker, data in results if data is not None}
        valid_data.update(batch_data)
        
        # Small sleep between batches
        time.sleep(2)
    
    if valid_data:
        df = pd.DataFrame(valid_data)
        df.sort_index(inplace=True)
        print(f"\nSuccessfully fetched {len(df.columns)} tickers")
        print(f"Date range: {df.index.min().date()} to {df.index.max().date()}")
        
        df.to_parquet('market_prices_stooq.parquet', compression='snappy')
        print("Data saved to 'market_prices_stooq.parquet'")
        return df
    else:
        raise ValueError("No valid data retrieved")

if __name__ == "__main__":
    try:
        price_data = main()
    except Exception as e:
        print(f"An error occurred: {e}")