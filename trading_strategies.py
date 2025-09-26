class MomentumStrategy:
    def __init__(self, williamR_buy = -80, williamR_sell = -20, rsi_buy = 30, rsi_sell = 70):
        self.williamR_buy = williamR_buy
        self.williamR_sell = williamR_sell
        self.rsi_buy = rsi_buy
        self.rsi_sell = rsi_sell
    
    def get_buy_sell_condition(self, day):
        william_oversold = day["William_R"] >= self.williamR_buy
        william_overbought = day["William_R"] <= self.williamR_sell
        williamR_crosses_up = (day["Previous_William_R"] < self.williamR_buy) & (day["William_R"] >= self.williamR_buy)
        williamR_crosses_down = (day["Previous_William_R"] > self.williamR_sell) & (day["William_R"] <= self.williamR_sell)
        rsi_increasing = day["10_Prior_RSI"] < day["RSI"]
        rsi_decreasing = day["10_Prior_RSI"] > day["RSI"]
        #rsi_crosses_up = (day["Previous_RSI"] < self.rsi_buy) & (day["RSI"] >= self.rsi_buy)
        #rsi_crosses_down = (day["Previous_RSI"] > self.rsi_sell) & (day["RSI"] <= self.rsi_sell)
        buy_condition = (rsi_increasing & william_oversold) #| williamR_crosses_up
        sell_condition = (rsi_decreasing & william_overbought) #| williamR_crosses_down
        return buy_condition, sell_condition
    