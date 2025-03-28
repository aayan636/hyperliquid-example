from typing import Tuple, Literal, Optional, Union

from pydantic import BaseModel


class ChainOrder(BaseModel):
    oid: Optional[str]
    is_buy: bool
    size: float
    coin: Literal["HYPE"]
    position: float
    order_type: dict
    reduce_only: bool

    def __hash__(self) -> int:
        return self.oid.__hash__() + self.is_buy.__hash__() + self.coin.__hash__() + self.position.__hash__() + self.reduce_only.__hash__()

class ChainOrderSet(BaseModel):
    orders: Tuple[ChainOrder, ...]
    next_order_set: Optional["ChainOrderSet"] = None

    def __hash__(self) -> int:
        return self.orders.__hash__()

class Strategy(BaseModel):
    mode: Union[Literal["LONG"], Literal["SHORT"]]
    sz: float
    coin: Literal["HYPE"]
    px: float
    stoploss: Optional[float] = None
    takeprofit: Optional[float] = None
