from datetime import datetime, timedelta

from contexts.base import Context
from constants.constants import COIN, SECOND_TO_MS, SECONDS_PER_DAY

from hyperliquid.info import Info

class PriceHistoryContext(Context):
    def __init__(self, info: Info):
        self.info = info
        self.data = None

    def fetch_data(self) -> None:
        current_time = datetime.now()
        one_hour_ago = current_time - timedelta(hours=1)
        self.data = self.info.candles_snapshot(
            COIN, 
            "1h", 
            int(current_time.timestamp()) * SECOND_TO_MS - SECONDS_PER_DAY * SECOND_TO_MS, 
            int(one_hour_ago.timestamp())*SECOND_TO_MS
        )

    def context_for_llm(self, *args, **kwargs) -> str:
        processed_strings = '\n'.join([f'{datetime.fromtimestamp(row["T"]/1000.0)}\t{row["o"]}\t{row["c"]}\t{row["v"]}\t{row["c"]}' for row in self.data])
        return f"""
        Price History Context
        ---------------------
        TimeStamp\tOpen Price\tClose Price\tVariance\tNumber Of Transactions
        {processed_strings}
        """