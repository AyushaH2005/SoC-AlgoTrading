from src.backtester import Order, OrderBook
from typing import List

class Trader:

    def run(self, state, current_position):
        result = {} # stores your orders

        orders: List[Order] = [] # append Order objects to the list
        order_depth: OrderBook = state.order_depth # get orderbook (has sell and buy orders)
        best_ask = list(order_depth.sell_orders.items())[0][0] if order_depth.sell_orders else None
        best_bid = list(order_depth.buy_orders.items())[0][0] if order_depth.buy_orders else None

        mid_price = (best_bid + best_ask) / 2
        spread = best_ask - best_bid
        
        
        buy_price = mid_price - spread/2
        sell_price = mid_price + spread/2
        if order_depth.sell_orders:
            best_ask, best_ask_amt = list(order_depth.sell_orders.items())[0]
            orders.append(Order("PRODUCT", buy_price, -best_ask_amt))
            best_bid, best_bid_amt = list(order_depth.buy_orders.items())[0]
            orders.append(Order("PRODUCT", sell_price, -best_bid_amt))

        result["PRODUCT"] = orders
        return result