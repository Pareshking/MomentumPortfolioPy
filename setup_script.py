#!/usr/bin/env python3
"""
Setup and Run Script for Momentum Portfolio Manager
This script helps set up the environment and provides easy commands to run the portfolio manager.
"""

import subprocess
import sys
import os
from datetime import datetime

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False
    return True

def create_sample_config():
    """Create a sample configuration file"""
    config = {
        "max_stocks": 30,
        "exit_rank": 60,
        "dma_period": 200,
        "lookback_periods": [3, 6, 9, 12],
        "high_percentage_threshold": 30,
        "use_all_time_high": False,
        "portfolio_file": "current_portfolio.json",
        "data_cache_file": "stock_data_cache.json"
    }
    
    import json
    with open('portfolio_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Created sample configuration file: portfolio_config.json")

def show_menu():
    """Show the main menu"""
    print("\n" + "="*60)
    print("MOMENTUM PORTFOLIO MANAGER")
    print("="*60)
    print("1. Setup Environment (Install packages)")
    print("2. Run Monthly Rebalancing")
    print("3. Run Daily Monitoring")
    print("4. Show Current Configuration")
    print("5. Create Sample Configuration")
    print("6. Exit")
    print("="*60)

def run_rebalancing():
    """Run the monthly rebalancing"""
    print(f"\n🔄 Starting Monthly Rebalancing - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        import momentum_portfolio
        portfolio_manager = momentum_portfolio.MomentumPortfolioManager()
        results = portfolio_manager.rebalance_portfolio()
        
        # Save results
        filename = f'rebalance_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        import json
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✅ Rebalancing completed! Results saved to: {filename}")
        
    except Exception as e:
        print(f"❌ Error during rebalancing: {e}")

def run_monitoring():
    """Run the daily monitoring"""
    print(f"\n👁️  Starting Daily Monitoring - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        import momentum_portfolio
        portfolio_manager = momentum_portfolio.MomentumPortfolioManager()
        results = portfolio_manager.daily_monitoring()
        
        # Save results
        filename = f'monitoring_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        import json
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✅ Monitoring completed! Results saved to: {filename}")
        
    except Exception as e:
        print(f"❌ Error during monitoring: {e}")

def show_config():
    """Show current configuration"""
    try:
        import json
        if os.path.exists('portfolio_config.json'):
            with open('portfolio_config.json', 'r') as f:
                config = json.load(f)
            print("\n📋 Current Configuration:")
            print(json.dumps(config, indent=2))
        else:
            print("❌ Configuration file not found. Please create one first.")
    except Exception as e:
        print(f"❌ Error reading configuration: {e}")

def main():
    """Main function"""
    while True:
        show_menu()
        
        try:
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == '1':
                install_requirements()
                
            elif choice == '2':
                run_rebalancing()
                
            elif choice == '3':
                run_monitoring()
                
            elif choice == '4':
                show_config()
                
            elif choice == '5':
                create_sample_config()
                
            elif choice == '6':
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please enter 1-6.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ An error occurred: {e}")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
