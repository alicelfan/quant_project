import numpy as np
import pandas as pd
from trade import Trades
from trading_strategies import MomentumStrategy

def simulate_trades(train, williamR_buy, williamR_sell, rsi_buy, rsi_sell):
    trade_obj = Trades()
    portfolio_values = []
    portfolio_dates = []
    strategy = MomentumStrategy(williamR_buy, williamR_sell, rsi_buy, rsi_sell)
    for _, day in train.iterrows():
        trade_obj.reset_entry_allowed()
        if pd.isna(day["Next_Open"]):
            continue
        trade_obj.set_next_price_date(day["Next_Open"], day["Next_Date"])
        
        buy_condition, sell_condition = strategy.get_buy_sell_condition(day)
        if (day["Week"] != trade_obj.current_week) or (day["Year"] != trade_obj.current_year):
            trade_obj.reset_week(day["Week"], day["Year"])
        
        # stop loss or take profit
        trade_obj.exit_stoploss_takegain(day["Close"])
        # trade_obj.exit_holding_max()
        trade_obj.exit_position(buy_condition, sell_condition)
            
        trade_obj.enter_market(buy_condition, sell_condition)
        # trade_obj.increment_holding_days()

        portfolio_value = trade_obj.get_portfolio_value()
        portfolio_values.append(portfolio_value)
        portfolio_dates.append(day["Date"])
    trade_obj.exit_end()
    portfolio_series = pd.Series(portfolio_values, index=portfolio_dates)
    # trade_obj.print()
    return trade_obj.trades, portfolio_series, trade_obj.cash

def scorer(X, williamR_buy, williamR_sell, rsi_buy, rsi_sell, interval="day"):
    trades, portfolio_series, end_cash = simulate_trades(X, williamR_buy, williamR_sell, rsi_buy, rsi_sell)
    pnl = pnl_calculator(trades) 
    if (interval == "day"):
        periods_per_year = 252
    elif (interval == "week"):
        periods_per_year = 52
    sharpe_ratio = sharpe_score(portfolio_series, periods_per_year)
    return pnl, sharpe_ratio

def pnl_calculator(trades):
    return sum(trade["PNL"] for trade in trades)

def sharpe_score(portfolio_series, periods_per_year):
    returns = portfolio_series.pct_change().dropna()
    mean_return = returns.mean()
    std_return =  np.std(returns, ddof=1)
    if std_return != 0:
        sharpe_ratio = mean_return / std_return * np.sqrt(periods_per_year)
    else:
        return np.nan
    return sharpe_ratio
