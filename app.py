import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# ---------------------------- Constants and Configurations ---------------------------- #

ASSET_DESCRIPTIONS = {
    'SPY': 'S&P 500 ETF',
    'QQQ': 'Nasdaq 100 ETF',
    'IWM': 'Russell 2000 ETF',
    'IJR': 'S&P Small-Cap ETF',
    'IJH': 'S&P Mid-Cap ETF',
    'IWF': 'Russell 1000 Growth ETF',
    'IWD': 'Russell 1000 Value ETF',
    'EFA': 'Developed Markets ETF',
    'EWJ': 'Japan ETF',
    'FXI': 'China ETF',
    'EWG': 'Germany ETF',
    'EEM': 'Emerging Markets ETF',
    'EWZ': 'Brazil ETF',
    'INDA': 'India ETF',
    'EWT': 'Taiwan ETF',
    'EWY': 'South Korea ETF',
    'EWW': 'Mexico ETF',
    'TLT': '20+ Year Treasury ETF',
    'IEF': '7-10 Year Treasury ETF',
    'LQD': 'Investment Grade Bond ETF',
    'HYG': 'High Yield Bond ETF',
    'BND': 'Total Bond Market ETF',
    'TIP': 'TIPS Bond ETF',
    'UUP': 'US Dollar ETF',
    'FXE': 'Euro ETF',
    'XLF': 'Financial Select Sector SPDR Fund',
    'XLK': 'Technology Select Sector SPDR Fund',
    'XLE': 'Energy Select Sector SPDR Fund',
    'XLV': 'Health Care Select Sector SPDR Fund',
    'XLI': 'Industrial Select Sector SPDR Fund',
    'XLP': 'Consumer Staples Select Sector SPDR Fund',
    'XLY': 'Consumer Discretionary Select Sector SPDR Fund',
    'XLB': 'Materials Select Sector SPDR Fund',
    'XLC': 'Communication Services Select Sector SPDR Fund',
    'XLU': 'Utilities Select Sector SPDR Fund',
    'VNQ': 'Real Estate ETF',
    'GLD': 'Gold ETF',
    'SLV': 'Silver ETF',
    'USO': 'Oil ETF',
    'UNG': 'Natural Gas ETF',
    'DBC': 'Commodity Index ETF',
    'BTC': 'Bitcoin'
}

TIMEFRAMES = {
    '1M': '1 Month',
    '3M': '3 Months',
    '6M': '6 Months',
    '1Y': '1 Year'
}

TRADING_DAYS_PER_YEAR = 252

# ---------------------------- Page Configuration ---------------------------- #

st.set_page_config(
    page_title="Cross-Asset Correlation Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------- Custom CSS for Enhanced Styling ---------------------------- #

st.markdown("""
    <style>
    /* Import Google Fonts - Added Playfair Display for WSJ-like style */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Roboto:wght@400;700&display=swap');

    /* General App Styling */
    .stApp {
        background-color: #0a0a1a;
        color: #ecf0f1;
        font-family: 'Roboto', sans-serif;
    }

    /* Header Styling - Updated with Playfair Display */
    .header {
        text-align: center;
        font-size: 3rem;
        color: #ecf0f1;
        font-weight: 700;
        margin-bottom: 0.5rem;
        font-family: 'Playfair Display', serif;
        letter-spacing: -0.5px;
    }

    /* Subheader Styling - Enhanced */
    .subheader {
        text-align: center;
        font-size: 1.6rem;
        color: #00A3FF;
        font-weight: 800;
        margin-bottom: 2rem;
        font-family: 'Playfair Display', serif;
        letter-spacing: -0.3px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }

    /* Selectbox Labels */
    .stSelectbox > label {
        font-weight: 700;
        font-size: 1.1rem;
        color: #ecf0f1;
        font-family: 'Playfair Display', serif;
    }

    /* Selectbox Styling */
    .stSelectbox > div > div > select {
        background-color: #2a2a45;
        color: #ecf0f1;
        border: 4px solid #00A3FF;
        border-radius: 8px;
        padding: 0.6rem;
        font-size: 1rem;
        font-weight: 700;
    }

    /* Button Styling */
    .stButton > button {
        background-color: #DC143C;
        color: white;
        border: none;
        padding: 0.7rem 1.5rem;
        border-radius: 8px;
        font-size: 1rem;
        font-weight: 700;
        cursor: pointer;
        font-family: 'Roboto', sans-serif;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: background-color 0.3s, transform 0.2s;
    }

    .stButton > button:hover {
        background-color: #8B0000;
        transform: translateY(-2px);
    }

    /* Plotly Graph Container */
    .chart-container {
        border: none;
        border-radius: 12px;
        padding: 1rem;
        margin-top: 2%;
        background-color: #1e1e2f;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        overflow: hidden;
        width: 100%;
        box-sizing: border-box;
    }

    .chart-container > div {
        width: 100% !important;
        height: 600px !important;
    }

    /* Correlation Metric Boxes */
    .corr-box {
        background-color: #2a2a45;
        border: 4px solid #00A3FF;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        margin: 0 auto;
    }

    .corr-box h4 {
        color: #95a5a6;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
        font-weight: 700;
        font-family: 'Playfair Display', serif;
    }

    .corr-box h3 {
        color: #32CD32;
        font-size: 1.6rem;
        font-weight: 700;
        font-family: 'Playfair Display', serif;
    }

    /* Footer Styling */
    .footer {
        text-align: center;
        color: #95a5a6;
        font-size: 0.9rem;
        margin-top: 3rem;
    }

    /* Responsive Design */
    @media (max-width: 1200px) {
        .header {
            font-size: 2.5rem;
        }
        .subheader {
            font-size: 1.4rem;
        }
    }

    @media (max-width: 768px) {
        .header {
            font-size: 2rem;
        }
        .subheader {
            font-size: 1.2rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)
# ---------------------------- Data Loading with Caching ---------------------------- #

@st.cache_data(show_spinner=True, ttl=3600)  # Cached for 1 hour
def load_data(corr_path: str, prices_path: str):
    """
    Load correlation matrix and market prices data from parquet files.
    """
    try:
        corr_matrix = pd.read_parquet(corr_path)
        prices = pd.read_parquet(prices_path)
        
        if not isinstance(prices.index, pd.DatetimeIndex):
            prices.index = pd.to_datetime(prices.index)
        
        return corr_matrix, prices
    except FileNotFoundError as fnf_error:
        st.error(f"File not found: {fnf_error.filename}. Please ensure the data files are present.")
        st.stop()
    except pd.errors.EmptyDataError:
        st.error("One of the data files is empty. Please provide valid data.")
        st.stop()
    except Exception as e:
        st.error(f"An unexpected error occurred while loading data: {e}")
        st.stop()

# ---------------------------- Load Data ---------------------------- #

corr_matrix, prices = load_data('correlation_matrix.parquet', 'market_prices_stooq.parquet')

# ---------------------------- Header and Asset Setup ---------------------------- #

missing_assets = set(prices.columns.unique()) - set(ASSET_DESCRIPTIONS.keys())
if missing_assets:
    for asset in missing_assets:
        ASSET_DESCRIPTIONS[asset] = 'Unknown Asset'

assets = sorted(prices.columns.unique())
asset_options = [f"{asset} ({ASSET_DESCRIPTIONS.get(asset, 'Unknown Asset')})" for asset in assets]

st.markdown("""
    <div class="header">Cross-Asset Correlation Dashboard</div>
    <div class="subheader">Analyze the volatility-adjusted and rolling correlations between various financial assets</div>
    """, unsafe_allow_html=True)

# ---------------------------- Date Range and Asset Selection ---------------------------- #

end_date = prices.index.max()
start_date = end_date - pd.DateOffset(years=3)
filtered_prices = prices.loc[start_date:end_date].copy()

expected_trading_days = TRADING_DAYS_PER_YEAR * 3
actual_trading_days = len(filtered_prices)

if actual_trading_days < expected_trading_days * 0.8:
    st.warning(f"Insufficient data for a 3-year analysis. Expected at least {int(expected_trading_days * 0.8)} trading days, but found {actual_trading_days} trading days.")

col1, col2 = st.columns(2)

with col1:
    default_asset1 = 'SPY (S&P 500 ETF)' if 'SPY (S&P 500 ETF)' in asset_options else asset_options[0]
    asset1_full = st.selectbox(
        "Select Asset 1",
        options=asset_options,
        index=asset_options.index(default_asset1)
    )
    asset1 = asset1_full.split(' (')[0]

with col2:
    default_asset2 = 'BTC (Bitcoin)' if 'BTC (Bitcoin)' in asset_options else (asset_options[1] if len(asset_options) > 1 else asset_options[0])
    asset2_full = st.selectbox(
        "Select Asset 2",
        options=asset_options,
        index=asset_options.index(default_asset2) if default_asset2 in asset_options else (1 if len(asset_options) > 1 else 0)
    )
    asset2 = asset2_full.split(' (')[0]

if asset1 == asset2:
    st.warning("Please select two different assets for comparison.")

# ---------------------------- Correlation Calculation ---------------------------- #

def calculate_volatility_based_correlations(prices_df: pd.DataFrame, asset_a: str, asset_b: str, timeframes: dict):
    correlations = {}
    for tf_key, tf_name in timeframes.items():
        window_days = {
            '1M': 21,
            '3M': 63,
            '6M': 126,
            '1Y': 252
        }.get(tf_key, 252)

        rolling_std_a = prices_df[asset_a].pct_change().rolling(window=window_days).std()
        rolling_std_b = prices_df[asset_b].pct_change().rolling(window=window_days).std()
        window_data = pd.concat([rolling_std_a, rolling_std_b], axis=1).dropna()

        if len(window_data) >= window_days * 0.8:
            corr_value = window_data[asset_a].corr(window_data[asset_b])
            correlations[tf_key] = corr_value
        else:
            correlations[tf_key] = None

    return correlations

volatility_correlations = calculate_volatility_based_correlations(filtered_prices, asset1, asset2, TIMEFRAMES)

columns = st.columns(len(TIMEFRAMES))

for idx, (tf_key, tf_name) in enumerate(TIMEFRAMES.items()):
    corr = volatility_correlations.get(tf_key)
    if corr is not None:
        color = '#2ECC71' if corr >= 0 else '#E74C3C'
        corr_display = f"{corr:.2f}"
    else:
        color = '#95a5a6'
        corr_display = "N/A"

    with columns[idx]:
        st.markdown(f"""
            <div class="corr-box">
                <h4>{tf_name}</h4>
                <h3 style="color: {color};">{corr_display}</h3>
            </div>
        """, unsafe_allow_html=True)

# ---------------------------- Calculate Rolling Metrics ---------------------------- #

returns_a = filtered_prices[asset1].pct_change()
returns_b = filtered_prices[asset2].pct_change()
rolling_corr_30 = returns_a.rolling(window=30).corr(returns_b)
rolling_corr_90 = returns_a.rolling(window=90).corr(returns_b)
rolling_corr_30 = rolling_corr_30.dropna()
rolling_corr_90 = rolling_corr_90.dropna()

# ---------------------------- Create Plotly Figures ---------------------------- #

def create_price_figure(prices_df: pd.DataFrame, asset1: str, asset2: str, asset_descriptions: dict):
    fig = go.Figure()
    
    normalized_prices = prices_df.copy()
    normalized_prices[asset1] = prices_df[asset1] / prices_df[asset1].iloc[0]
    normalized_prices[asset2] = prices_df[asset2] / prices_df[asset2].iloc[0]
    
    fig.add_trace(
        go.Scatter(
            x=normalized_prices.index,
            y=normalized_prices[asset1],
            name=f"{asset1} ({asset_descriptions.get(asset1, 'Unknown')})",
            line=dict(color='#00A3FF', width=3, dash='solid'),  # Bright Azure
            mode='lines+markers',
            marker=dict(size=6, symbol='circle'),
            hovertemplate='<b>%{text}</b><br>Date: %{x|%Y-%m-%d}<br>Normalized Price: %{y:.2f}<extra></extra>',
            text=[f"{asset1}"]*len(normalized_prices)
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=normalized_prices.index,
            y=normalized_prices[asset2],
            name=f"{asset2} ({asset_descriptions.get(asset2, 'Unknown')})",
            line=dict(color='#DC143C', width=3, dash='dash'),
            mode='lines+markers',
            marker=dict(size=6, symbol='triangle-up'),
            hovertemplate='<b>%{text}</b><br>Date: %{x|%Y-%m-%d}<br>Normalized Price: %{y:.2f}<extra></extra>',
            text=[f"{asset2}"]*len(normalized_prices)
        )
    )
    
    fig.update_layout(
        template="plotly_dark",
        title=dict(
            text="Normalized Price Performance",
            font=dict(family="Playfair Display, serif", size=24)
        ),
        height=600,
        margin=dict(l=50, r=50, t=50, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(family="Playfair Display, serif", color="#ecf0f1")
        ),
        plot_bgcolor='#1e1e2f',
        paper_bgcolor='#1e1e2f',
        font=dict(family="Playfair Display, serif", color="#ecf0f1"),
        hovermode='x unified'
    )
    
    fig.update_yaxes(
        title_text="Normalized Price",
        gridcolor='#444465',
        zerolinecolor='#444465',
        title_font=dict(family="Playfair Display, serif", size=14),
        tickfont=dict(family="Playfair Display, serif", size=12, color="#ecf0f1")
    )
    
    fig.update_xaxes(
        title_text="",
        gridcolor='#444465',
        zerolinecolor='#444465',
        tickfont=dict(family="Playfair Display, serif", size=12, color="#ecf0f1"),
        rangeslider=dict(visible=False)
    )
    
    return fig

def create_correlation_figure(rolling_corr_30: pd.Series, rolling_corr_90: pd.Series):
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=rolling_corr_30.index,
            y=rolling_corr_30,
            name="30-Day Rolling Correlation",
            line=dict(color='#00A3FF', width=1.5),  # Bright Azure
            hovertemplate='<b>30-Day Rolling Correlation</b><br>Date: %{x|%Y-%m-%d}<br>Correlation: %{y:.2f}<extra></extra>'
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=rolling_corr_90.index,
            y=rolling_corr_90,
            name="90-Day Rolling Correlation",
            line=dict(color='#DC143C', width=1.5, dash='dash'),
            hovertemplate='<b>90-Day Rolling Correlation</b><br>Date: %{x|%Y-%m-%d}<br>Correlation: %{y:.2f}<extra></extra>'
        )
    )
    
    fig.update_layout(
        template="plotly_dark",
        title=dict(
            text="Rolling Correlation",
            font=dict(family="Playfair Display, serif", size=24)
        ),
        height=600,
        margin=dict(l=50, r=50, t=50, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(family="Playfair Display, serif", color="#ecf0f1")
        ),
        plot_bgcolor='#1e1e2f',
        paper_bgcolor='#1e1e2f',
        font=dict(family="Playfair Display, serif", color="#ecf0f1"),
        hovermode='x unified'
    )
    
    fig.update_yaxes(
        title_text="Correlation",
        range=[-1, 1],
        gridcolor='#444465',
        zerolinecolor='#444465',
        title_font=dict(family="Playfair Display, serif", size=14),
        tickfont=dict(family="Playfair Display, serif", size=12, color="#ecf0f1")
    )
    
    fig.update_xaxes(
        title_text="",
        gridcolor='#444465',
        zerolinecolor='#444465',
        tickfont=dict(family="Playfair Display, serif", size=12, color="#ecf0f1"),
        rangeslider=dict(visible=False)
    )
    
    return fig

# Create and display figures
fig_price = create_price_figure(filtered_prices, asset1, asset2, ASSET_DESCRIPTIONS)
fig_corr = create_correlation_figure(rolling_corr_30, rolling_corr_90)

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.plotly_chart(fig_price, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with col_chart2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.plotly_chart(fig_corr, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------- Footer ---------------------------- #

st.markdown(f"""
    <div class="footer">
        &copy; {datetime.now().year} Omar Abdeljabar. All rights reserved.
    </div>
    """, unsafe_allow_html=True)





