from src.backtester import Order, OrderBook
from typing import List

class Trader:
    def _init_(self):
        self.position = 0

    def run(self, state, current_position):
        result = {}
        orders: List[Order] = []
        order_depth: OrderBook = state.order_depth

        best_ask = sorted(order_depth.sell_orders.items())[0][0] if order_depth.sell_orders else None
        best_bid = sorted(order_depth.buy_orders.items(), reverse=True)[0][0] if order_depth.buy_orders else None

        if best_ask is None or best_bid is None:
            return {}

        # Set size and buffer for safety margin
        order_size = 5
        spread_buffer = 1  # you can tune this

        # Market making: place buy near bid, sell near ask
        orders.append(Order("PRODUCT", best_bid, order_size))    # Buy at bid
        orders.append(Order("PRODUCT", best_ask, -order_size))   # Sell at ask

        result["PRODUCT"] = orders
        return result