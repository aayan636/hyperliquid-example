from contexts.base import Context
from hyperliquid.utils.types import L2BookMsg
from hyperliquid.info import Info
from constants.constants import COIN


class CurrentBookContext(Context):

    def __init__(self, info: Info):
        self.info = info
        self.data = None

    def fetch_data(self) -> None:
        self.data = self.info.l2_snapshot(COIN)

    def context_for_llm(self) -> str:
        ask_book_data = self.data["levels"][0]
        ask_entries = '\n'.join([f'{entry["px"]}\t{entry["sz"]}\t{entry["n"]}' for entry in ask_book_data])

        bid_book_data = self.data["levels"][1]
        bid_entries = '\n'.join([f'{entry["px"]}\t{entry["sz"]}\t{entry["n"]}' for entry in bid_book_data])

        context_string = f"""
        Current Book Context
        --------------------
        Asking Bids
        Position\tSize\tCount
        {ask_entries}

        Buying Bids
        Position\tSize\tCount
        {bid_entries}
        """

        return context_string
        