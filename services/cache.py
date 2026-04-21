from datetime import datetime

cache = {
    "nbk_price": None,
    "binance_info": None,
    "bybit_info": None,
    "updated_at": None
}

def update_cache(nbk_price, binance_info, bybit_info):
    cache["nbk_price"] = nbk_price
    cache["binance_info"] = binance_info
    cache["bybit_info"] = bybit_info
    cache["updated_at"] = datetime.now().isoformat()

def get_cache():
    return cache