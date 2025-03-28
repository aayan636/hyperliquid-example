import threading
import time
from typing import Dict
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from constants.constants import POLLING_TIME_PERIOD
from trade.data_model import Strategy, ChainOrderSet, ChainOrder

class OrderQueue:
    def __init__(self, info: Info, exchange: Exchange):
        self.exchange = exchange
        self.info = info
        self.oid_to_order_set: Dict[str, ChainOrderSet] = {}
        self._start_poller()

    def _start_poller(self) -> None:
        """Start the polling thread for checking open orders and positions."""
        self.poller = threading.Thread(target=self._poll, daemon=True)
        self.poller.start()

    def enqueue_strategy(self, strategy: Strategy):
        first_order_set = ChainOrderSet(orders=(ChainOrder(
            oid = None,
            is_buy=(strategy.mode == "LONG"),
            size=strategy.sz,
            coin=strategy.coin,
            position=strategy.px,
            order_type={
                "limit": {"tif": "Gtc"},  # Limit order, Good 'Til Canceled
            },
            reduce_only=False
        ),))
       
        second_orders = []
        if strategy.takeprofit:
            second_orders.append(ChainOrder(
                oid=None,
                is_buy=(strategy.mode != "LONG"),
                size=strategy.sz,
                coin=strategy.coin,
                position=strategy.px,
                order_type={
                    "trigger": {
                        "triggerPx": strategy.takeprofit,  # Trigger price for TP
                        "isMarket": True,  # Execute as market order when TP is hit
                        "tpsl": "tp",  # Take Profit order
                    }
                },
                reduce_only=True
            ))
        
        if strategy.stoploss:
            second_orders.append(ChainOrder(
                oid=None,
                is_buy=(strategy.mode != "LONG"),
                size=strategy.sz,
                coin=strategy.coin,
                position=strategy.px,
                order_type={
                    "trigger": {
                        "triggerPx": strategy.stoploss,  # Trigger price for TP
                        "isMarket": True,  # Execute as market order when TP is hit
                        "tpsl": "sl",  # Take Profit order
                    }
                },
                reduce_only=True
            ))
        
        if second_orders:
            second_order_set = ChainOrderSet(orders=tuple(second_orders))
            first_order_set.next_order_set = second_order_set

        self.enqueue_order(first_order_set)
        if second_orders:
            self.enqueue_order(second_order_set)


    def enqueue_order(self, order_set: ChainOrderSet):
        for order in order_set.orders:
            response = self.exchange.order(name=order.coin, is_buy=order.is_buy, sz=order.size, limit_px=order.position, order_type=order.order_type, reduce_only=order.reduce_only)
            assert response["status"] == "ok"
            status = response["response"]["data"]["statuses"][0]
            # assert status == "resting"
            oid = list(status.values())[0]["oid"]
            order.oid = oid
            self.oid_to_order_set[oid] = order_set

    def _poll(self):
        while True:
            open_orders = self.info.open_orders(self.exchange.wallet.address)
            open_order_ids = {open_order["oid"] for open_order in open_orders}
            record_open_orders = set(self.oid_to_order_set.keys())
            closed_order_ids = record_open_orders.difference(open_order_ids)

            order_sets_to_close = {self.oid_to_order_set[closed_order_id] for closed_order_id in closed_order_ids}
            new_order_sets_to_open = {order_set.next_order_set for order_set in order_sets_to_close if order_set.next_order_set}

            cancel_requests = []
            for order_set_to_close in order_sets_to_close:
                for order in order_set_to_close.orders:
                    cancel_requests.append({"coin": order.coin, "oid": order.oid})
            cancel_requests = cancel_requests

            self.exchange.bulk_cancel(cancel_requests)
            
            for order_set in new_order_sets_to_open:
                self.enqueue_order(order_set)
            time.sleep(POLLING_TIME_PERIOD)
        

