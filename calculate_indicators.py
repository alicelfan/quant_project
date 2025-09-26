import matplotlib.pyplot as plt 
import numpy as np
import pandas as pd
def calculate_avg(rsi_window, values):
    avg = []
    for i in range(len(values)):
        if i < (rsi_window - 1):
            avg.append(np.nan)
        elif i == (rsi_window - 1):
            avg.append(np.mean(values[:rsi_window]))
        else:
            prev_avg = avg[-1]
            new_sum = prev_avg * (rsi_window - 1) + values[i]
            avg.append(new_sum / rsi_window)
    return avg

def calculate_rsi(financial_data, rsi_window):
    # calculate gains and losses
    financial_data["Gain"] = financial_data["Close"].diff().apply(lambda x: x if x > 0 else 0)
    financial_data["Loss"] = financial_data["Close"].diff().apply(lambda x: -x if x < 0 else 0)
    
    # calculate average gains and losses
    financial_data["Average Gain"] = calculate_avg(rsi_window, np.array(financial_data.Gain))
    financial_data["Average Loss"] = calculate_avg(rsi_window, np.array(financial_data.Loss))

    # calculate rsi
    financial_data["RSI"] = 100 - (100 / (1 + financial_data["Average Gain"] / financial_data["Average Loss"]))
    financial_data["10_Prior_RSI"] = financial_data["RSI"].shift(10)
    financial_data["Previous_RSI"] = financial_data["RSI"].shift(1)
    return financial_data

def plot_rsi(financial_data, overbought_threshold=30, oversold_threshold=70, rsi_window=14):
    plt.plot(financial_data.Date, financial_data.RSI)
    plt.axhline(y=overbought_threshold, color='red', linestyle='--', linewidth=1, label=f'Overbought ({overbought_threshold})')
    plt.axhline(y=oversold_threshold, color='green', linestyle='--', linewidth=1, label=f'Oversold ({oversold_threshold})')
    plt.title(f"{rsi_window}-Day RSI")
    plt.xlabel("Date")
    plt.ylabel("RSI")
    plt.legend()
    plt.ylim(0, 100)
    plt.tight_layout()
    plt.show()

def calculate_williams_r(financial_data, william_r_window):
    # calculate highest high and lowest low
    financial_data["Highest_High"] = financial_data["High"].rolling(william_r_window).max()
    financial_data["Lowest_Low"] = financial_data["Low"].rolling(william_r_window).min()

    # calculate William's R
    financial_data["William_R"] = (financial_data["Highest_High"] - financial_data["Close"]) / (financial_data["Highest_High"] - financial_data["Lowest_Low"]) * (-100)
    return financial_data

def plot_williams_r(financial_data, overbought_threshold=-20, oversold_threshold=-80, william_r_window=14):
    plt.plot(financial_data.Date, financial_data.William_R)
    plt.axhline(y=overbought_threshold, color='red', linestyle='--', linewidth=1, label=f'Overbought ({overbought_threshold})')
    plt.axhline(y=oversold_threshold, color='green', linestyle='--', linewidth=1, label=f'Oversold ({oversold_threshold})')
    plt.title(f"{william_r_window}-Day William's R")
    plt.xlabel("Date")
    plt.ylabel("William's R")
    plt.legend()
    plt.ylim(-105, 5)
    plt.tight_layout()
    plt.show()

def calculate_indicators(financial_data, rsi_window=14, william_r_window=14):
    rsi_data = calculate_rsi(financial_data, rsi_window)
    final_data = calculate_williams_r(rsi_data, william_r_window)
    final_data["Previous_William_R"] = final_data["William_R"].shift(1)
    final_data.drop(columns=["Gain", "Loss", "Average Gain", "Average Loss", "Highest_High", "Lowest_Low"], inplace = True)
    return final_data