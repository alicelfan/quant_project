import pandas as pd

class Trades:
    def __init__(self, trade_limit = 2, holding_max = 5, stop_loss = -0.02, take_profit = 0.05, start_cash = 100000):
        self.WEEKLY_TRADE_LIMIT = trade_limit
        self.MAX_HOLDING_DAYS = holding_max
        self.STOP_LOSS = stop_loss
        self.TAKE_PROFIT = take_profit
        
        self.trades = []
        self.cash = start_cash
        self.position_size = 0
        self.position = "None"
        self.entry_price = None
        self.entry_date = None
        self.next_day_price = None
        self.next_day = None

        self.current_week = None
        self.current_year = None
        self.weekly_trade_count = 0
        self.holding_days = 0
        self.entry_allowed = True

    def print(self):
        trades_df = pd.DataFrame.from_dict(self.trades)
        print(trades_df)
    
    def reset_entry_allowed(self):
        self.entry_allowed = True
        return 
    
    def reset_position(self):
        self.position = "None"
        self.entry_price = None
        self.entry_date = None
        self.holding_days = 0
        self.weekly_trade_count += 1
        self.entry_allowed = False
        self.position_size = 0
        return

    def reset_week(self, week, year):
        self.current_week = week
        self.current_year = year
        self.weekly_trade_count = 0
        return
    
    def add_trade(self, reason):
        if self.position == "None": 
            print("invalid; adding trade when entering")
            return
        pnl = (self.next_day_price - self.entry_price) * self.position_size if self.position == "Long" \
            else (self.entry_price - self.next_day_price) * self.position_size
        if self.position == "Long":
            self.cash += self.position_size * self.next_day_price
        else:
            self.cash -= self.position_size * self.next_day_price
        trade = {
            "Entry Date": self.entry_date,
            "Exit Date": self.next_day,
            "PNL": pnl,
            "Reason": reason,
        }
        self.trades.append(trade)
        return 
    
    def increment_holding_days(self):
        if self.position != "None":
            self.holding_days += 1 
        return

    def set_next_price_date(self, next_price, next_date):
        self.next_day_price = next_price
        self.next_day = next_date
        return
    
    def update_position_cash(self):
        if (self.position == "None"): return
        calculated_position_size = min((self.cash * 0.05) / abs(self.STOP_LOSS), self.cash)
        calculated_share_amt = calculated_position_size // self.next_day_price
        self.position_size = calculated_share_amt
        if (self.position == "Long"):
            self.cash -= self.position_size * self.next_day_price
        else:
            self.cash += self.position_size * self.next_day_price
        
    def enter_market(self, buy_condition, sell_condition):
        below_trade_limit = self.weekly_trade_count < self.WEEKLY_TRADE_LIMIT
        if self.position == "None" and self.entry_allowed and below_trade_limit:
            if (buy_condition):
                self.position = "Long"
            elif (sell_condition):
                self.position = "Short"
            if self.position != "None":
                self.update_position_cash()
                self.entry_price = self.next_day_price
                self.entry_date = self.next_day
                self.weekly_trade_count += 1
                self.holding_days = 0
        return
    
    def exit_stoploss_takegain(self, conditional_price):
        if self.position == "None": return
        pnl_pct = (conditional_price - self.entry_price) / self.entry_price  if self.position == "Long" \
            else (self.entry_price - conditional_price) / self.entry_price
        if (pnl_pct >= self.TAKE_PROFIT): 
            self.add_trade("Take Profit")
            self.reset_position()
        elif pnl_pct <= self.STOP_LOSS:
            self.add_trade("Stop Loss")
            self.reset_position()
        return
    
    def exit_holding_max(self):
        if self.position == "None": return
        if (self.holding_days >= self.MAX_HOLDING_DAYS):
            self.add_trade("Holding Limit Reached")
            self.reset_position()
        return

    def exit_position(self, buy_condition, sell_condition):
        if self.position == "None": return
        below_trade_limit = self.weekly_trade_count < self.WEEKLY_TRADE_LIMIT
        if self.position == "Long":
            if sell_condition and below_trade_limit:
                self.add_trade(self.position)
                self.reset_position()
        elif self.position == "Short":
            if buy_condition and below_trade_limit:
                self.add_trade(self.position)
                self.reset_position()
        return

    def exit_end(self):
        if self.position == "None": return
        self.add_trade(self.position)
        self.reset_position()
        return
    
    def get_portfolio_value(self):
        if self.position == "None":
            market_value = 0
        else:
            market_value = self.position_size * self.next_day_price
        return self.cash + market_value