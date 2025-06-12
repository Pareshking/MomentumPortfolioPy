# 🚀 Momentum Portfolio Manager

An automated momentum-based portfolio management system for NSE stocks using Python.

## 📋 Features

- **Automated Stock Screening**: Filters stocks based on momentum criteria
- **Sharpe Ratio Calculation**: Multi-period Sharpe ratio analysis (3/6/9/12 months)
- **Technical Filters**: 200-day moving average and 52-week high proximity checks
- **Portfolio Construction**: Automatically builds portfolios with up to 30 stocks
- **Daily Monitoring**: Tracks portfolio stocks for 200 DMA breaks
- **Monthly Rebalancing**: Automated monthly portfolio rebalancing
- **JSON Configuration**: Easily configurable parameters

## 🔧 Setup Instructions

### 1. Prerequisites
- Python 3.7 or higher
- Internet connection for fetching stock data

### 2. Installation

1. Download all the files to a folder:
   - `momentum_portfolio.py` (main script)
   - `setup_and_run.py` (setup helper)
   - `requirements.txt` (dependencies)
   - Batch files for automation

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Or use the setup script:
   ```bash
   python setup_and_run.py
   ```

### 3. Configuration

The system uses a `portfolio_config.json` file for configuration:

```json
{
  "max_stocks": 30,
  "exit_rank": 60,
  "dma_period": 200,
  "lookback_periods": [3, 6, 9, 12],
  "high_percentage_threshold": 30,
  "use_all_time_high": false,
  "portfolio_file": "current_portfolio.json",
  "data_cache_file": "stock_data_cache.json"
}
```

**Configuration Parameters:**
- `max_stocks`: Maximum number of stocks in portfolio (default: 30)
- `exit_rank`: Exit rank threshold (default: 60)
- `dma_period`: Moving average period (default: 200)
- `lookback_periods`: Sharpe ratio calculation periods in months
- `high_percentage_threshold`: Maximum distance from 52-week high (%)
- `use_all_time_high`: Use all-time high instead of 52-week high
- `portfolio_file`: File to store current portfolio
- `data_cache_file`: File to cache stock data

## 🎯 Usage

### Method 1: Command Line
```bash
# Monthly rebalancing
python momentum_portfolio.py rebalance

# Daily monitoring
python momentum_portfolio.py monitor

# Show configuration
python momentum_portfolio.py config
```

### Method 2: Interactive Menu
```bash
python setup_and_run.py
```

### Method 3: Batch Files (Windows)
- Double-click `run_rebalance.bat` for monthly rebalancing
- Double-click `run_monitor.bat` for daily monitoring

### Method 4: Shell Scripts (Linux/Mac)
```bash
# Make executable
chmod +x run_rebalance.sh run_monitor.sh

# Run scripts
./run_rebalance.sh    # Monthly rebalancing
./run_monitor.sh      # Daily monitoring
```

## 📊 Portfolio Strategy

### Screening Criteria
1. **Technical Filter**: Stock price > 200-day moving average
2. **Momentum Filter**: Stock within 30% of 52-week high (configurable)
3. **Sharpe Ratio**: Ranked by 12-month Sharpe ratio
4. **Universe**: NSE stocks (expandable to NSE 750)

### Portfolio Rules
- **Maximum 30 stocks** in portfolio
- **Monthly rebalancing** on predetermined dates
- **Daily exit monitoring** for 200 DMA breaks
- **Immediate exit** when stock breaks below 200 DMA
- **New additions** only on rebalance days

### Sharpe Ratio Calculation
1. Fetch daily price data for specified lookback period
2. Calculate daily returns
3. Compute annualized return and volatility
4. Sharpe Ratio = Annualized Return / Annualized Volatility

## 📁 File Structure

```
momentum_portfolio/
├── momentum_portfolio.py       # Main portfolio manager
├── setup_and_run.py           # Setup and interactive runner
├── requirements.txt           # Python dependencies
├── portfolio_config.json     # Configuration file
├── current_portfolio.json    # Current portfolio data
├── run_rebalance.bat         # Windows rebalance script
├── run_monitor.bat           # Windows monitoring script
├── run_rebalance.sh          # Linux/Mac rebalance script
├── run_monitor.sh            # Linux/Mac monitoring script
├── rebalance_results_*.json  # Rebalancing results
└── monitoring_results_*.json # Daily monitoring results
```

## 🔄 Automation Setup

### Windows Task Scheduler
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger for monthly rebalancing
4. Set action to run `run_rebalance.bat`
5. Repeat for daily monitoring with `run_monitor.bat`

### Linux/Mac Cron Jobs
```bash
# Edit crontab
crontab -e

# Add these lines:
# Daily monitoring at 9:30 AM
30 9 * * 1-5 /path/to/your/script/run_monitor.sh

# Monthly rebalancing on 1st of each month at 10:00 AM
0 10 1 * * /path/to/your/script/run_rebalance.sh
```

## 📈 Output Examples

### Rebalancing Output
```
==============================================================
MOMENTUM PORTFOLIO REBALANCING
==============================================================
Fetching data for 50 stocks...
✓ RELIANCE.NS (1/50)
✓ TCS.NS (2/50)
...
Screening stocks...

📊 REBALANCING RESULTS
📈 New Portfolio Size: 30 stocks
➕ Added Stocks: 5
➖ Removed Stocks: 3

🆕 ADDED STOCKS:
   • TITAN.NS
   • MARUTI.NS
   • SUNPHARMA.NS

🗑️  REMOVED STOCKS:
   • ONGC.NS
   • COALINDIA.NS

📋 FINAL PORTFOLIO:
    1. RELIANCE.NS
    2. TCS.NS
    3. HDFCBANK.NS
    ...
```

### Daily Monitoring Output
```
==============================================================
DAILY PORTFOLIO MONITORING
==============================================================
Checking DMA breaks...
🟢 RELIANCE.NS - Above 200 DMA (Price: 2450.00, DMA: 2380.50)
🟢 TCS.NS - Above 200 DMA (Price: 3890.00, DMA: 3750.25)
🔴 ONGC.NS - Below 200 DMA (Price: 185.50, DMA: 195.75)

📊 MONITORING RESULTS
📈 Portfolio Size: 30 stocks
🔴 Stocks Below 200 DMA: 1
🟢 Healthy Stocks: 29

⚠️  STOCKS TO EXIT (Below 200 DMA):
   • ONGC.NS
```

## 🛠️ Customization

### Adding More Stocks
To expand beyond the sample tickers, modify the `get_nse_tickers()` method in `momentum_portfolio.py`:

```python
def get_nse_tickers(self) -> List[str]:
    # Add your NSE 750 tickers here
    your_tickers = [
        'RELIANCE', 'TCS', 'HDFCBANK', 
        # ... add all 750 tickers
    ]
    return [ticker + '.NS' for ticker in your_tickers]
```

### Adjusting Parameters
Modify `portfolio_config.json`:
- Change `max_stocks` for different portfolio sizes
- Adjust `high_percentage_threshold` for different momentum criteria
- Modify `lookback_periods` for different Sharpe calculation windows
- Set `use_all_time_high: true` to use all-time highs instead of 52-week highs

### Adding New Filters
Extend the `screen_stocks()` method to add custom filters:

```python
# Example: Add volume filter
avg_volume = data['Volume'].tail(20).mean()
if avg_volume < 100000:  # Minimum volume threshold
    continue
```

## 🚨 Important Notes

### Data Limitations
- Uses Yahoo Finance data (free but may have delays)
- Sample includes ~50 stocks (expand to NSE 750 for production)
- Historical data availability may vary by stock

### Risk Considerations
- **Backtesting**: Always backtest before live trading
- **Market Conditions**: Strategy performance varies with market conditions
- **Slippage**: Consider transaction costs and slippage
- **Position Sizing**: Implement proper position sizing rules

### Error Handling
- System handles missing data gracefully
- Logs errors for individual stock processing
- Continues processing even if some stocks fail

## 📞 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   pip install --upgrade yfinance pandas numpy requests
   ```

2. **Data Fetch Failures**
   - Check internet connection
   - Verify ticker symbols are correct
   - Some stocks may be delisted or suspended

3. **Configuration Errors**
   - Ensure `portfolio_config.json` is valid JSON
   - Check file permissions for writing results

4. **Empty Portfolio**
   - Relax screening criteria
   - Check if stocks meet all filters
   - Verify data availability for selected time periods

### Debug Mode
Add debugging by modifying the script:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔄 Updating the System

### Adding New Features
1. Fork the code
2. Add new methods to the `MomentumPortfolioManager` class
3. Update configuration schema if needed
4. Test thoroughly before production use

### Version Control
Consider using Git for tracking changes:
```bash
git init
git add .
git commit -m "Initial momentum portfolio setup"
```

## 📚 Additional Resources

- [NSE Website](https://www.nseindia.com/) - Official NSE data
- [Yahoo Finance API](https://pypi.org/project/yfinance/) - Data source documentation
- [Pandas Documentation](https://pandas.pydata.org/docs/) - Data manipulation
- [NumPy Documentation](https://numpy.org/doc/) - Numerical computing

## ⚖️ Disclaimer

This software is for educational and research purposes only. It is not investment advice. Always:
- Consult with financial advisors
- Understand the risks involved
- Test thoroughly before real trading
- Consider your risk tolerance
- Past performance doesn't guarantee future results

---

**Happy Trading! 🚀📈**