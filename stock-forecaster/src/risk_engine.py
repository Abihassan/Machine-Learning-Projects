import logging

# Set up logging to track trades
logging.basicConfig(filename='logs/trading.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def calculate_exit_levels(entry_price: float, stop_loss_pct: float = 0.02, take_profit_pct: float = 0.05):
    """Calculates risk levels based on entry price."""
    stop_loss = entry_price * (1 - stop_loss_pct)
    take_profit = entry_price * (1 + take_profit_pct)
    return stop_loss, take_profit

def validate_trade_risk(account_balance: float, trade_amount: float):
    """Ensures we aren't risking too much of the portfolio."""
    if trade_amount > (account_balance * 0.10):
        logging.warning("Trade size exceeds 10% of portfolio. Rejected.")
        return False
    return True