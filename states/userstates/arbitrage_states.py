from enum import Enum


class DefaultStart(Enum):
    INVOKE = "0"


class CryptoArbitrage(Enum):
    GET_ORDER = "1"
    GET_COUNTS = "2"


class CryptoArbitrageFull(Enum):
    START_ARBITRAGE = "1"
