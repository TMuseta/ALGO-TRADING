import alpaca_trade_api as tradeapi
from tabulate import tabulate
import time
import math

# Set up your Alpaca API credentials
API_KEY = 'AKIOSNT4Y3DH4HLGDJUY'
API_SECRET = 'l5CdzMfThSeH9Q9tTFaG5Ybkd1ZvuplxtKJf9Xs0'
BASE_URL = 'https://api.alpaca.markets'  # Paper trading base URL, replace with live trading URL if applicable

# Connect to the Alpaca API
api = tradeapi.REST(API_KEY, API_SECRET, base_url=BASE_URL, api_version='v2')

# Define a function to get account details in dollar value
def get_account_details():
    account = api.get_account()
    cash = float(account.cash)
    buying_power = float(account.buying_power)
    equity = float(account.equity)
    account_details = {
        'Cash': f'${cash:.2f}',
        'Buying Power': f'${buying_power:.2f}',
        'Equity': f'${equity:.2f}'
    }
    return account_details

# Define your trading strategy

def trading_strategy(symbol):
    try:
        # Get the current price and previous day's close price
        current_price = float(api.get_latest_trade(symbol).price)

        # Get the list of positions
        positions = api.list_positions()

        if not any(position.symbol == symbol for position in positions):
            # No position exists, place a limit buy order
            limit_price = current_price * 0.995  # Limit price set to 99.5% of the current price

            # Round the limit price to the nearest valid increment
            limit_price = round(limit_price, 2)  # Assuming 2 decimal places

            if limit_price <= current_price:
                # Place a limit buy order at the rounded limit price
                api.submit_order(
                    symbol=symbol,
                    qty=2,  # Specify the quantity you want to buy
                    side='buy',
                    type='limit',
                    limit_price=limit_price,
                    time_in_force='gtc'
                )
                action = 'Buy (Limit)'
            else:
                action = 'Hold'
            profit_percentage = 0  # No position, so profit percentage is 0
        else:
            # A position exists, calculate profit percentage
            position = next(position for position in positions if position.symbol == symbol)
            average_cost = float(position.avg_entry_price)
            profit_percentage = ((current_price - average_cost) / average_cost) * 100

            # Sell all stocks when a profit of 30 to 35% is made
            if profit_percentage >= 30 and profit_percentage <= 35:
                # Place a limit sell order at the current price or higher
                api.submit_order(
                    symbol=symbol,
                    qty=int(position.qty),
                    side='sell',
                    type='limit',
                    limit_price=current_price,
                    time_in_force='gtc'
                )
                action = 'Sell'
            else:
                action = 'Hold'

        # Track trading activities
        trading_activities = [
            {
                'Timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'Symbol': symbol,
                'Action': action,
                'Price': f'${current_price:.2f}',
                'Profit %': f'{profit_percentage:.2f}%'
            }
        ]

        return trading_activities

    except Exception as e:
        print(f'Error: {e}')
        return []
# Main function
def main():
    symbol = 'CVNA'  # Replace with the desired symbol
    while True:
        # Get account details and trading activities
        account_details = get_account_details()
        activities = trading_strategy(symbol)

        # Combine account details and trading activities
        combined_data = [account_details] + activities

        # Print combined data in a table
        print('Account Details and Trading Activities:')
        print(tabulate(combined_data, headers='keys', tablefmt='rounded_grid'))
        print()

        # Check if a sell order is executed
        if activities and activities[-1]['Action'] == 'Sell':
            print('Profit target achieved. Sell order executed.')

        # Sleep for 1 minute before updating again
        time.sleep(60)

# Run the main function
if __name__ == '__main__':
    main()
