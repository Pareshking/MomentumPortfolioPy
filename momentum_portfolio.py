import yfinance as yf
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
import requests
from typing import List, Dict, Tuple
import warnings
warnings.filterwarnings('ignore')

class MomentumPortfolioManager:
    def __init__(self, config_file='portfolio_config.json'):
        """
        Initialize the Momentum Portfolio Manager
        
        Args:
            config_file: JSON file containing portfolio configuration
        """
        self.config_file = config_file
        self.load_config()
        
    def load_config(self):
        """Load or create configuration file"""
        default_config = {
            "max_stocks": 30,
            "exit_rank": 60,
            "dma_period": 200,
            "lookback_periods": [3, 6, 9, 12],  # months
            "high_percentage_threshold": 30,  # % from 52-week high
            "use_all_time_high": False,  # Set to True to use all-time high instead
            "portfolio_file": "current_portfolio.json",
            "data_cache_file": "stock_data_cache.json"
        }
        
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get_nse_tickers(self) -> List[str]:
        """
        Get NSE tickers. For now, using a representative list.
        In production, you'd scrape from NSE or use their API.
        """
        # This is a sample list - you should replace with actual NSE 750 tickers
        sample_tickers = [
            'RELIANCE', 'TCS', 'HDFCBANK', 'BHARTIARTL', 'ICICIBANK',
            'SBIN', 'LICI', 'ITC', 'HINDUNILVR', 'LT', 'KOTAKBANK',
            'AXISBANK', 'ASIANPAINT', 'MARUTI', 'SUNPHARMA', 'TITAN',
            'ULTRACEMCO', 'DMART', 'BAJFINANCE', 'HCLTECH', 'WIPRO',
            'ADANIENT', 'ONGC', 'TATAMOTORS', 'POWERGRID', 'NTPC',
            'JSWSTEEL', 'TATASTEEL', 'COALINDIA', 'INDUSINDBK', 'GRASIM',
            'BAJAJFINSV', 'HDFCLIFE', 'SBILIFE', 'TECHM', 'HINDALCO',
            'ADANIPORTS', 'BRITANNIA', 'NESTLEIND', 'DRREDDY', 'CIPLA',
            'APOLLOHOSP', 'DIVISLAB', 'EICHERMOT', 'HEROMOTOCO', 'BAJAJ-AUTO',
            'PIDILITIND', 'GODREJCP', 'MARICO', 'DABUR', 'COLPAL',
        ]
        
        # Add .NS suffix for Yahoo Finance
        return [ticker + '.NS' for ticker in sample_tickers]
    
    def fetch_stock_data(self, tickers: List[str], period: str = '2y') -> Dict[str, pd.DataFrame]:
        """
        Fetch stock data for given tickers
        
        Args:
            tickers: List of stock tickers
            period: Data period (1y, 2y, etc.)
        
        Returns:
            Dictionary of ticker -> DataFrame
        """
        stock_data = {}
        
        print(f"Fetching data for {len(tickers)} stocks...")
        for i, ticker in enumerate(tickers):
            try:
                data = yf.download(ticker, period=period, progress=False)
                if not data.empty:
                    # FIX: Handle MultiIndex columns from yfinance
                    if isinstance(data.columns, pd.MultiIndex):
                        data.columns = data.columns.droplevel(1)
                    stock_data[ticker] = data
                    print(f"✓ {ticker} ({i+1}/{len(tickers)})")
                else:
                    print(f"✗ {ticker} - No data available")
            except Exception as e:
                print(f"✗ {ticker} - Error: {str(e)}")
        
        return stock_data
    
    def calculate_sharpe_ratio(self, data: pd.DataFrame, months: int) -> float:
        """
        Calculate Sharpe ratio for given period
        
        Args:
            data: Stock price data
            months: Lookback period in months
        
        Returns:
            Sharpe ratio
        """
        try:
            if len(data) < months * 21:  # Approximate trading days per month
                return np.nan
            
            # Get data for the specified period
            end_date = data.index[-1]
            start_date = end_date - timedelta(days=months * 30)
            period_data = data[data.index >= start_date]
            
            if len(period_data) < 2:
                return np.nan
            
            # FIX: Ensure we're working with Series
            close_prices = period_data['Close']
            if isinstance(close_prices, pd.DataFrame):
                close_prices = close_prices.iloc[:, 0]
            
            # Calculate daily returns
            returns = close_prices.pct_change().dropna()
            
            if len(returns) < 2:
                return np.nan
            
            # Calculate annualized return
            start_price = close_prices.iloc[0]
            end_price = close_prices.iloc[-1]
            
            # FIX: Convert to scalar if needed
            if isinstance(start_price, pd.Series):
                start_price = start_price.iloc[0] if len(start_price) > 0 else np.nan
            if isinstance(end_price, pd.Series):
                end_price = end_price.iloc[0] if len(end_price) > 0 else np.nan
            
            if pd.isna(start_price) or pd.isna(end_price) or start_price == 0:
                return np.nan
            
            total_return = (float(end_price) / float(start_price)) - 1
            annualized_return = (1 + total_return) ** (12 / months) - 1
            
            # Calculate annualized volatility
            daily_volatility = returns.std()
            if pd.isna(daily_volatility) or daily_volatility == 0:
                return np.nan
            
            annualized_volatility = float(daily_volatility) * np.sqrt(252)
            
            # Calculate Sharpe ratio (assuming 0 risk-free rate)
            if annualized_volatility == 0:
                return np.nan
            
            return annualized_return / annualized_volatility
        except Exception as e:
            print(f"Error calculating Sharpe ratio: {str(e)}")
            return np.nan
    
    def calculate_dma(self, data: pd.DataFrame, period: int = 200) -> float:
        """Calculate Daily Moving Average"""
        try:
            if len(data) < period:
                return np.nan
            
            # FIX: Ensure we're working with Series, not DataFrame
            close_prices = data['Close']
            if isinstance(close_prices, pd.DataFrame):
                close_prices = close_prices.iloc[:, 0]  # Take first column if DataFrame
            
            dma_value = close_prices.rolling(window=period).mean().iloc[-1]
            
            # FIX: Convert to scalar if it's a Series
            if isinstance(dma_value, pd.Series):
                dma_value = dma_value.iloc[0] if len(dma_value) > 0 else np.nan
            
            return float(dma_value) if not pd.isna(dma_value) else np.nan
        except Exception as e:
            print(f"Error calculating DMA: {str(e)}")
            return np.nan
    
    def calculate_52week_high_distance(self, data: pd.DataFrame) -> float:
        """Calculate distance from 52-week high"""
        try:
            if len(data) < 252:
                high_period = len(data)
            else:
                high_period = 252
            
            recent_data = data.tail(high_period)
            
            # FIX: Ensure we're working with Series
            high_prices = recent_data['High']
            close_prices = data['Close']
            
            if isinstance(high_prices, pd.DataFrame):
                high_prices = high_prices.iloc[:, 0]
            if isinstance(close_prices, pd.DataFrame):
                close_prices = close_prices.iloc[:, 0]
            
            high_52week = high_prices.max()
            current_price = close_prices.iloc[-1]
            
            # FIX: Convert to scalar if needed
            if isinstance(high_52week, pd.Series):
                high_52week = high_52week.iloc[0] if len(high_52week) > 0 else np.nan
            if isinstance(current_price, pd.Series):
                current_price = current_price.iloc[0] if len(current_price) > 0 else np.nan
            
            if pd.isna(high_52week) or pd.isna(current_price) or high_52week == 0:
                return np.nan
            
            return ((float(high_52week) - float(current_price)) / float(high_52week)) * 100
        except Exception as e:
            print(f"Error calculating 52-week high distance: {str(e)}")
            return np.nan
    
    def calculate_all_time_high_distance(self, data: pd.DataFrame) -> float:
        """Calculate distance from all-time high"""
        try:
            # FIX: Ensure we're working with Series
            high_prices = data['High']
            close_prices = data['Close']
            
            if isinstance(high_prices, pd.DataFrame):
                high_prices = high_prices.iloc[:, 0]
            if isinstance(close_prices, pd.DataFrame):
                close_prices = close_prices.iloc[:, 0]
            
            all_time_high = high_prices.max()
            current_price = close_prices.iloc[-1]
            
            # FIX: Convert to scalar if needed
            if isinstance(all_time_high, pd.Series):
                all_time_high = all_time_high.iloc[0] if len(all_time_high) > 0 else np.nan
            if isinstance(current_price, pd.Series):
                current_price = current_price.iloc[0] if len(current_price) > 0 else np.nan
            
            if pd.isna(all_time_high) or pd.isna(current_price) or all_time_high == 0:
                return np.nan
            
            return ((float(all_time_high) - float(current_price)) / float(all_time_high)) * 100
        except Exception as e:
            print(f"Error calculating all-time high distance: {str(e)}")
            return np.nan
    
    def screen_stocks(self, stock_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Screen stocks based on momentum criteria
        
        Args:
            stock_data: Dictionary of stock data
        
        Returns:
            DataFrame with screened stocks and their metrics
        """
        results = []
        
        print("Screening stocks...")
        for ticker, data in stock_data.items():
            try:
                if len(data) < self.config['dma_period']:
                    continue
                
                # FIX: Ensure we get scalar values
                close_prices = data['Close']
                if isinstance(close_prices, pd.DataFrame):
                    close_prices = close_prices.iloc[:, 0]
                
                current_price = close_prices.iloc[-1]
                if isinstance(current_price, pd.Series):
                    current_price = current_price.iloc[0] if len(current_price) > 0 else np.nan
                
                if pd.isna(current_price):
                    continue
                
                current_price = float(current_price)
                dma_200 = self.calculate_dma(data, self.config['dma_period'])
                
                # FIX: Check for NaN before comparison
                if pd.isna(dma_200) or current_price <= dma_200:
                    continue
                
                # Check distance from high
                if self.config['use_all_time_high']:
                    high_distance = self.calculate_all_time_high_distance(data)
                else:
                    high_distance = self.calculate_52week_high_distance(data)
                
                # FIX: Also check high_distance for NaN
                if pd.isna(high_distance) or high_distance > self.config['high_percentage_threshold']:
                    continue
                
                # Calculate Sharpe ratios for different periods
                sharpe_ratios = {}
                for months in self.config['lookback_periods']:
                    sharpe_ratios[f'sharpe_{months}m'] = self.calculate_sharpe_ratio(data, months)
                
                # Use 12-month Sharpe as primary ranking metric
                primary_sharpe = sharpe_ratios.get('sharpe_12m', np.nan)
                
                if pd.isna(primary_sharpe):
                    continue
                
                result = {
                    'ticker': ticker,
                    'current_price': current_price,
                    'dma_200': float(dma_200),
                    'high_distance': float(high_distance),
                    'primary_sharpe': float(primary_sharpe),
                    **{k: float(v) if not pd.isna(v) else np.nan for k, v in sharpe_ratios.items()}
                }
                
                results.append(result)
                
            except Exception as e:
                print(f"Error processing {ticker}: {str(e)}")
                continue
        
        if not results:
            return pd.DataFrame()
        
        df = pd.DataFrame(results)
        
        # Rank by primary Sharpe ratio
        df['sharpe_rank'] = df['primary_sharpe'].rank(ascending=False)
        
        # Sort by Sharpe ratio (descending)
        df = df.sort_values('primary_sharpe', ascending=False)
        
        return df
    
    def build_portfolio(self, screened_stocks: pd.DataFrame) -> List[str]:
        """
        Build portfolio from screened stocks
        
        Args:
            screened_stocks: DataFrame with screened stocks
        
        Returns:
            List of selected stock tickers
        """
        if screened_stocks.empty:
            return []
        
        # Select top stocks up to max_stocks limit
        selected_stocks = screened_stocks.head(self.config['max_stocks'])
        return selected_stocks['ticker'].tolist()
    
    def save_portfolio(self, portfolio: List[str]):
        """Save current portfolio to file"""
        portfolio_data = {
            'stocks': portfolio,
            'last_rebalance': datetime.now().isoformat(),
            'next_rebalance': (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        with open(self.config['portfolio_file'], 'w') as f:
            json.dump(portfolio_data, f, indent=2)
    
    def load_portfolio(self) -> Dict:
        """Load current portfolio from file"""
        if os.path.exists(self.config['portfolio_file']):
            with open(self.config['portfolio_file'], 'r') as f:
                return json.load(f)
        return {'stocks': [], 'last_rebalance': None, 'next_rebalance': None}
    
    def check_dma_breaks(self, portfolio_stocks: List[str]) -> List[str]:
        """
        Check which portfolio stocks have broken below 200 DMA
        
        Args:
            portfolio_stocks: List of stocks in current portfolio
        
        Returns:
            List of stocks that broke below 200 DMA
        """
        if not portfolio_stocks:
            return []
        
        stock_data = self.fetch_stock_data(portfolio_stocks, period='2y')
        broken_stocks = []
        
        print("Checking DMA breaks...")
        for ticker in portfolio_stocks:
            try:
                if ticker not in stock_data:
                    print(f"⚠️  {ticker} - No data available")
                    continue
                
                data = stock_data[ticker]
                if len(data) < self.config['dma_period']:
                    continue
                
                # FIX: Ensure we get scalar values
                close_prices = data['Close']
                if isinstance(close_prices, pd.DataFrame):
                    close_prices = close_prices.iloc[:, 0]
                
                current_price = close_prices.iloc[-1]
                if isinstance(current_price, pd.Series):
                    current_price = current_price.iloc[0] if len(current_price) > 0 else np.nan
                
                if pd.isna(current_price):
                    print(f"⚠️  {ticker} - Cannot get current price")
                    continue
                
                current_price = float(current_price)
                dma_200 = self.calculate_dma(data, self.config['dma_period'])
                
                # FIX: Check for NaN before comparison
                if pd.isna(dma_200):
                    print(f"⚠️  {ticker} - Cannot calculate DMA (insufficient data)")
                    continue
                
                if current_price < dma_200:
                    broken_stocks.append(ticker)
                    print(f"🔴 {ticker} - Below 200 DMA (Price: {current_price:.2f}, DMA: {dma_200:.2f})")
                else:
                    print(f"🟢 {ticker} - Above 200 DMA (Price: {current_price:.2f}, DMA: {dma_200:.2f})")
                    
            except Exception as e:
                print(f"Error checking {ticker}: {str(e)}")
                continue
        
        return broken_stocks
    
    def rebalance_portfolio(self) -> Dict:
        """
        Perform monthly portfolio rebalancing
        
        Returns:
            Dictionary with rebalancing results
        """
        print("=" * 60)
        print("MOMENTUM PORTFOLIO REBALANCING")
        print("=" * 60)
        
        # Get all tickers
        tickers = self.get_nse_tickers()
        
        # Fetch stock data
        stock_data = self.fetch_stock_data(tickers)
        
        # Screen stocks
        screened_stocks = self.screen_stocks(stock_data)
        
        if screened_stocks.empty:
            print("No stocks passed the screening criteria!")
            return {'success': False, 'message': 'No stocks passed screening'}
        
        # Build new portfolio
        new_portfolio = self.build_portfolio(screened_stocks)
        
        # Load current portfolio
        current_portfolio_data = self.load_portfolio()
        current_portfolio = current_portfolio_data.get('stocks', [])
        
        # Save new portfolio
        self.save_portfolio(new_portfolio)
        
        # Prepare results
        results = {
            'success': True,
            'rebalance_date': datetime.now().isoformat(),
            'new_portfolio': new_portfolio,
            'previous_portfolio': current_portfolio,
            'added_stocks': list(set(new_portfolio) - set(current_portfolio)),
            'removed_stocks': list(set(current_portfolio) - set(new_portfolio)),
            'screening_results': screened_stocks.to_dict('records')
        }
        
        # Print results
        print(f"\n📊 REBALANCING RESULTS")
        print(f"📈 New Portfolio Size: {len(new_portfolio)} stocks")
        print(f"➕ Added Stocks: {len(results['added_stocks'])}")
        print(f"➖ Removed Stocks: {len(results['removed_stocks'])}")
        
        if results['added_stocks']:
            print(f"\n🆕 ADDED STOCKS:")
            for stock in results['added_stocks']:
                print(f"   • {stock}")
        
        if results['removed_stocks']:
            print(f"\n🗑️  REMOVED STOCKS:")
            for stock in results['removed_stocks']:
                print(f"   • {stock}")
        
        print(f"\n📋 FINAL PORTFOLIO:")
        for i, stock in enumerate(new_portfolio, 1):
            print(f"   {i:2d}. {stock}")
        
        return results
    
    def daily_monitoring(self) -> Dict:
        """
        Perform daily monitoring of portfolio stocks
        
        Returns:
            Dictionary with monitoring results
        """
        print("=" * 60)
        print("DAILY PORTFOLIO MONITORING")
        print("=" * 60)
        
        # Load current portfolio
        portfolio_data = self.load_portfolio()
        portfolio_stocks = portfolio_data.get('stocks', [])
        
        if not portfolio_stocks:
            print("No stocks in current portfolio!")
            return {'success': False, 'message': 'No stocks in portfolio'}
        
        # Check for DMA breaks
        broken_stocks = self.check_dma_breaks(portfolio_stocks)
        
        results = {
            'success': True,
            'monitoring_date': datetime.now().isoformat(),
            'portfolio_size': len(portfolio_stocks),
            'broken_stocks': broken_stocks,
            'healthy_stocks': list(set(portfolio_stocks) - set(broken_stocks))
        }
        
        # Print results
        print(f"\n📊 MONITORING RESULTS")
        print(f"📈 Portfolio Size: {len(portfolio_stocks)} stocks")
        print(f"🔴 Stocks Below 200 DMA: {len(broken_stocks)}")
        print(f"🟢 Healthy Stocks: {len(results['healthy_stocks'])}")
        
        if broken_stocks:
            print(f"\n⚠️  STOCKS TO EXIT (Below 200 DMA):")
            for stock in broken_stocks:
                print(f"   • {stock}")
        else:
            print(f"\n✅ All portfolio stocks are above 200 DMA!")
        
        return results

def main():
    """Main function to run the portfolio manager"""
    import sys
    
    portfolio_manager = MomentumPortfolioManager()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python momentum_portfolio.py rebalance    # Monthly rebalancing")
        print("  python momentum_portfolio.py monitor      # Daily monitoring")
        print("  python momentum_portfolio.py config       # Show configuration")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'rebalance':
        results = portfolio_manager.rebalance_portfolio()
        
        # Save results to file
        with open(f'rebalance_results_{datetime.now().strftime("%Y%m%d")}.json', 'w') as f:
            json.dump(results, f, indent=2)
        
    elif command == 'monitor':
        results = portfolio_manager.daily_monitoring()
        
        # Save results to file
        with open(f'monitoring_results_{datetime.now().strftime("%Y%m%d")}.json', 'w') as f:
            json.dump(results, f, indent=2)
        
    elif command == 'config':
        print("Current Configuration:")
        print(json.dumps(portfolio_manager.config, indent=2))
        
    else:
        print(f"Unknown command: {command}")
        print("Use 'rebalance', 'monitor', or 'config'")

if __name__ == "__main__":
    main()