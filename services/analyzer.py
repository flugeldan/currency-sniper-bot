import asyncio
import sys
from typing import Optional
sys.path.insert(0, '/Users/se/Desktop/currency_sniper_bot')
from services.fetcher import get_nbk_rate, get_binance_p2p_rate
from datetime import datetime, timedelta

def calculate_arbitrage(nbk_price: float, p2p_info: tuple, exchange: str): 
    sellers, buyers = p2p_info[0], p2p_info[1]
    sellers_prices = [float(m['price']) for m in sellers]
    buyers_prices = [float(m['price']) for m in buyers]

    if len(sellers_prices) == 0:
        raise ValueError("Нету продавцов")
    elif len(buyers_prices) == 0:
        raise ValueError("Нету покупателей")
    
    best_spread_seller_price = max([abs(nbk_price - m) for m in sellers_prices])
    
    best_spread_buyers_price = max([abs(nbk_price - m) for m in buyers_prices])

    best_seller = max(sellers, key=lambda m: abs(nbk_price - m['price']))
    best_buyer = max(buyers, key=lambda m: abs(nbk_price - m['price']))

    if exchange == "binance":
        best_spread_seller_link = f"https://p2p.binance.com/en/advertiserDetail?advertiserNo={best_seller['user_no']}"
        best_spread_buyer_link = f"https://p2p.binance.com/en/advertiserDetail?advertiserNo={best_buyer['user_no']}"
    elif exchange == "bybit":
        best_spread_seller_link = f"https://www.bybit.com/en/p2p/order?userId={best_seller['user_no']}"
        best_spread_buyer_link = f"https://www.bybit.com/en/p2p/order?userId={best_buyer['user_no']}"
    
    avg_spread_sellers = sum([abs(nbk_price - m) for m in sellers_prices]) / len(sellers_prices)
    avg_spread_buyers = sum([abs(nbk_price - m) for m in buyers_prices]) / len(buyers_prices)

    info = {
        'best_seller': best_seller,
        'best_buyer': best_buyer,
        'best_spread_sellers_price': best_spread_seller_price,
        'best_spread_seller_link': best_spread_seller_link,
        'best_spread_buyers_price': best_spread_buyers_price,
        'best_spread_buyer_link': best_spread_buyer_link,
        'avg_spread_sellers': avg_spread_sellers,
        'avg_spread_buyers': avg_spread_buyers,
        'buy_sell_spread': buyers_prices[0] - sellers_prices[0], #покупателей
        'buy_sell_spread_percent': ((buyers_prices[0] - sellers_prices[0]) / sellers_prices[0]) * 100,
        'avg_spread_sellers_percent': (avg_spread_sellers / nbk_price) * 100, #авг от нбк
        'avg_spread_buyers_percent': (avg_spread_buyers / nbk_price) * 100, 
        'best_spread_seller_percent': (best_spread_seller_price / nbk_price) * 100,
        'best_spread_buyers_percent': (best_spread_buyers_price / nbk_price) * 100,
    }

    return info


def filter_best_merchants(merchants: list, min_completion_rate: float, min_orders:int, required_banks: set = None) -> Optional[list]:
    if not merchants:
        raise ValueError('Нету мерчантов')
    best_merchants = []
    for m in merchants:
        if m['monthFinishRate'] >= min_completion_rate and m['monthOrderCount'] >= min_orders:
            if required_banks is None:
                best_merchants.append(m)
            else:
                if required_banks & set(m['banks']) > 0:
                    best_merchants.append(m)
    return best_merchants # может быть пустым если никто не прошёл фильтр


def check_price_target(current_price: float, target_price: float, direction: str) -> bool:
    if direction == 'up':
        return current_price >= target_price
    else:
        return current_price <= target_price

    

def check_percent_target(current_price: float, initial_price: float, target_percent: float, direction: str) -> bool:
    actual_change = ((current_price - initial_price) / initial_price) * 100
    if direction == 'up':
        return actual_change >= target_percent
    else:
        return actual_change <= -target_percent #если падает то нам нужно либо равно либо меньше от того насколько нужно упасть

def is_outside_zone(current_price: float, last_triggered_price: float, zone_percent: float) -> bool:
    if last_triggered_price is None:
        return True 
    return abs(current_price - last_triggered_price) / last_triggered_price * 100 >= zone_percent

def is_outside_zone_by_spread(current_price: float, last_triggered_price: float, last_triggered_spread: float):
    if last_triggered_spread is None:
        return True
    return current_price - last_triggered_price >= last_triggered_spread



def is_cooldown_passed(last_triggered_at, cooldown_minutes: int = 30) -> bool:
    if last_triggered_at is None:
        return True
    last = datetime.fromisoformat(last_triggered_at)
    return datetime.now() - last > timedelta(minutes=cooldown_minutes)


async def test():
    nbk_rate = await get_nbk_rate("USD")
    p2p_info = await get_binance_p2p_rate()
    result = calculate_arbitrage(nbk_rate, p2p_info)
    print(f"НБК курс: {nbk_rate}")
    print(f"Лучший спред продавца: {result['best_spread_seller_price']}")
    print(f"Лучший продавец: {result['best_seller']['nickname']}")
    print(f"Ссылка: {result['best_spread_seller_link']}")
    print(f"Средний спред продавцов: {result['avg_spread_sellers']:.2f}")
    print(f"Buy/Sell спред: {result['buy_sell_spread']:.2f} KZT ({result['buy_sell_spread_percent']:.2f}%)")
    print(f"Средний спред sellers от НБК: {result['avg_spread_sellers']:.2f} ({result['avg_spread_sellers_percent']:.2f}%)")

