from src.backtester import Order, OrderBook
from typing import List
import numpy as np
import pandas as pd

class Trader:
    def __init__(self):
        self.price_history = []
        self.bb_width_history = []

    def run(self, state, current_position):
        result = {}

        orders: List[Order] = []
        order_depth: OrderBook = state.order_depth
        best_ask = sorted(order_depth.sell_orders.items())[0][0] if order_depth.sell_orders else None
        best_bid = sorted(order_depth.buy_orders.items(), reverse=True)[0][0] if order_depth.buy_orders else None
        
        if best_ask is not None and best_bid is not None:
            mid_price = (best_ask + best_bid) / 2
            self.price_history.append(mid_price)
        period = 20
        if len(self.price_history) > period:
            self.price_history.pop(0)
        #define SMA and calculate bollinger bands:
        
        def calculate_bollinger_bands():
            mean = np.mean(self.price_history)
            std = np.std(self.price_history)
            upper_band = mean + 2 * std
            lower_band = mean - 2 * std
            BB_width = upper_band - lower_band
            return BB_width
        #Determining Volataility
        
        VOL_WINDOW = 100
        BB_Width = calculate_bollinger_bands()
        self.bb_width_history.append(BB_Width)
        if len(self.bb_width_history) > VOL_WINDOW:
            self.bb_width_history.pop(0)
        if len(self.bb_width_history) == VOL_WINDOW:
            BB_Width_Median = pd.Series(self.bb_width_history).median()
            if BB_Width <BB_Width_Median:
                volatility = "LOW_VOLATILITY"     # Use Mean Reversion
            else:
                volatility = "HIGH_VOLATILITY"    # Use Breakout

            
            if volatility == "LOW_VOLATILITY":
                period = 20
                threshold = 1.05
                mean_price = np.mean(self.price_history)
                if order_depth.sell_orders:
                    best_ask, best_ask_amt = sorted(order_depth.sell_orders.items())[0]
                    if best_ask > mean_price*threshold :
                        orders.append(Order("PRODUCT", best_ask, -best_ask_amt))

                if order_depth.buy_orders:
                    best_bid, best_bid_amt = sorted(order_depth.buy_orders.items(), reverse=True)[0]
                    if best_bid < mean_price/threshold:
                        orders.append(Order("PRODUCT", best_bid, -best_bid_amt))

                
            if volatility == "HIGH_VOLATILITY":
                lookback = 20
                recent_high = max(self.price_history[-lookback:])
                recent_low = min(self.price_history[-lookback:])
                if order_depth.sell_orders:
                    best_ask, best_ask_amt = sorted(order_depth.sell_orders.items())[0]
                    if best_ask > recent_high:
                        orders.append(Order("PRODUCT", best_ask, -best_ask_amt))
                
                if order_depth.buy_orders:
                    best_bid, best_bid_amt = sorted(order_depth.buy_orders.items(), reverse=True)[0]
                    if best_bid <recent_low:
                        orders.append(Order("PRODUCT", best_bid, -best_bid_amt))
        

        result["PRODUCT"] = orders
        return result