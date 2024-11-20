import pandas as pd
import numpy as np
from itertools import combinations
from datetime import datetime

def calculate_all_correlations():
    print("Loading price data...")
    prices = pd.read_parquet('market_prices_stooq.parquet')
    
    # Calculate returns
    returns = prices.pct_change()
    
    # Get all unique pairs
    assets = prices.columns
    pairs = list(combinations(assets, 2))
    print(f"Calculating correlations for {len(pairs)} pairs...")
    
    # Define lookback periods
    lookbacks = {
        '1M': 21,
        '3M': 63,
        '6M': 126,
        '12M': 252
    }
    
    # Calculate correlations for each pair
    results = []
    for i, (asset1, asset2) in enumerate(pairs, 1):
        if i % 100 == 0:  # Progress update every 100 pairs
            print(f"Processing pair {i} of {len(pairs)}")
            
        row = {
            'Asset1': asset1,
            'Asset2': asset2
        }
        
        # Calculate correlation for each lookback period
        for period, days in lookbacks.items():
            corr = returns[asset1].rolling(days).corr(returns[asset2]).iloc[-1]
            row[f'Corr_{period}'] = round(corr, 3)
        
        results.append(row)
    
    # Convert to DataFrame
    corr_df = pd.DataFrame(results)
    
    # Save to parquet
    corr_df.to_parquet('correlation_matrix.parquet', compression='snappy')
    
    print("\nCorrelation Summary:")
    for period in lookbacks.keys():
        col = f'Corr_{period}'
        print(f"\n{period} Statistics:")
        print(f"Average correlation: {corr_df[col].mean():.3f}")
        print(f"Highest correlation: {corr_df[col].max():.3f}")
        print(f"Lowest correlation: {corr_df[col].min():.3f}")
    
    # Show some interesting pairs
    print("\nMost Correlated Pairs (1M):")
    print(corr_df.nlargest(5, 'Corr_1M')[['Asset1', 'Asset2', 'Corr_1M']])
    
    print("\nLeast Correlated Pairs (1M):")
    print(corr_df.nsmallest(5, 'Corr_1M')[['Asset1', 'Asset2', 'Corr_1M']])
    
    return corr_df

if __name__ == "__main__":
    try:
        correlation_data = calculate_all_correlations()
    except Exception as e:
        print(f"An error occurred: {e}")