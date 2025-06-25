from src.backtester import Order, OrderBook
from typing import List
import numpy as np

class Trader:
    def __init__(self):
        self.prices = []
        self.window = 20
        self.product = "PRODUCT"
        self.position_limit = 50

    def run(self, state, current_position):
        result = {}
        orders: List[Order] = []
        order_depth: OrderBook = state.order_depth

        if not order_depth.buy_orders or not order_depth.sell_orders:
            return result

        # Market snapshot
        best_bid = max(order_depth.buy_orders.keys())
        best_ask = min(order_depth.sell_orders.keys())
        mid_price = (best_bid + best_ask) / 2

        self.prices.append(mid_price)
        if len(self.prices) > self.window:
            self.prices.pop(0)
            
        if len(self.prices) < self.window:
            return result

        # Indicators
        prices_np = np.array(self.prices)
        sma = prices_np.mean()
        std = prices_np.std() or 1e-5
        z_score = (mid_price - sma) / std

        # Spread protection
        spread = best_ask - best_bid
        if spread < 1:
            spread = 1

        # Adjust prices based on inventory & skew
        inventory_skew = -0.03 * current_position
        fair_price = sma + inventory_skew
        bid_price = round(fair_price - spread / 2, 1)
        ask_price = round(fair_price + spread / 2, 1)

        # Define volumes safely
        best_bid_volume = list(order_depth.buy_orders.items())[-1][1]
        best_ask_volume = list(order_depth.sell_orders.items())[0][1]

        buy_volume = min(-best_ask_volume, self.position_limit - current_position)
        sell_volume = min(best_bid_volume, self.position_limit + current_position)

        # Z-score logic
        if z_score < -0.7 and buy_volume > 0:
            orders.append(Order(self.product, bid_price, -buy_volume))
        elif z_score > 0.7 and sell_volume > 0:
            orders.append(Order(self.product, ask_price, -sell_volume))

        # Passive MM if flat-ish
        if abs(z_score) < 0.4:
            passive_buy_vol = min(3, self.position_limit - current_position)
            passive_sell_vol = min(3, self.position_limit + current_position)
            orders.append(Order(self.product, round(fair_price - 1, 1), -passive_buy_vol))
            orders.append(Order(self.product, round(fair_price + 1, 1), -passive_sell_vol))

        # Profit exit logic (flatten when mean-reverted)
        if abs(current_position) > 0 and abs(z_score) < 0.2:
            if current_position > 0:
                orders.append(Order(self.product, best_ask, -current_position))
            elif current_position < 0:
                orders.append(Order(self.product, best_bid, -current_position))

        result[self.product] = orders
        return result
