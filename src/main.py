import logging
import time
from typing import List
from hyperliquid.utils import constants as hl_constants
from llm.basic_trading_agent import BasicTradingAgent
from contexts.base import Context
from constants.constants import LLM_TRADE_TIME_PERIOD_SECOND
from trade.order_queue import OrderQueue
from utils import hl_setup

from contexts import price_history, social_media, book

def main():
    # Setting this to logging.DEBUG can be helpful for debugging websocket callback issues
    logging.basicConfig(level=logging.INFO)
    info, exchange = hl_setup.setup(hl_constants.TESTNET_API_URL)
    contexts: List[Context] = [price_history.PriceHistoryContext(info=info), social_media.SocialMediaContext(), book.CurrentBookContext(info=info)]
    
    trader = BasicTradingAgent()
    orderer = OrderQueue(info, exchange)

    while True:
        all_contexts = ""
        for context in contexts:
            context.fetch_data()
            all_contexts += context.context_for_llm()
        strategy = trader.chat(all_contexts)
        orderer.enqueue_strategy(strategy)
        time.sleep(LLM_TRADE_TIME_PERIOD_SECOND) # Make o
    # BasicAdder(address, info, exchange)

if __name__ == "__main__":
    main()