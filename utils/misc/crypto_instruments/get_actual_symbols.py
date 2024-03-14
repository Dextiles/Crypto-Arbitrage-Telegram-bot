import ccxt


def get_actual_symbols(exchanges: list[str]) -> set[str]:
    """
    Generate a set of actual symbols based on the exchanges provided.

    Parameters:
    exchanges (list[str]): A list of exchange names.

    Returns:
    set[str]: A set of actual symbols.
    """
    actual_symbols = list()
    for current_exchange in [getattr(ccxt, exchange)() for exchange in exchanges]:
        try:
            current_exchange.load_markets()
            current_sym = [sym.split('/USDT')[0] for sym in list(filter(lambda sym: sym.endswith('/USDT'), current_exchange.symbols))]
        except Exception as ex:
            pass
        else:
            actual_symbols.extend(current_sym)
    return set(actual_symbols)
