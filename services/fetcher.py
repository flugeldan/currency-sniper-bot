import xml.etree.ElementTree as ET
import aiohttp
import asyncio
from typing import Optional


async def get_bybit_p2p_rate() -> Optional[tuple]:
    url = "https://www.bybit.com/x-api/fiat/otc/item/online"
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15",
        "lang": "ru-RU",
        "platform": "PC",
        "Referer": "https://www.bybit.com/ru-RU/p2p/buy/USDT/KZT",
        "Origin": "https://www.bybit.com",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={**_bybit_payload(), "side": "1"}, headers=headers) as r:
                sellers_info = await r.json()
            async with session.post(url, json={**_bybit_payload(), "side": "0"}, headers=headers) as r:
                buyers_info = await r.json()

        return (
            _bybit_parser(sellers_info["result"]["items"]),
            _bybit_parser(buyers_info["result"]["items"])
        )
    except Exception as e:
        print(f"Ошибка Bybit: {e}")
        return None


def _bybit_payload() -> dict:
    return {
        "userId": "", "tokenId": "USDT", "currencyId": "KZT",
        "payment": [], "size": "10", "page": "1", "amount": "",
        "vaMaker": False, "bulkMaker": False, "canTrade": False,
        "verificationFilter": 0, "sortType": "OVERALL_RANKING",
        "paymentPeriod": [], "itemRegion": 1
    }


def _bybit_parser(items: list) -> list:
    BYBIT_BANK_IDS = {
        "150": "Kaspi",
        "549": "Freedom",
        "203": "Halyk",
        }
    return [
        {
            "price": float(item["price"]),
            "nickname": item["nickName"],
            "orders": item["recentOrderNum"],
            "completion_rate": item["recentExecuteRate"],
            "min_amount": float(item["minAmount"]),
            "max_amount": float(item["maxAmount"]),
            "available": float(item["lastQuantity"]),
            "payments": item["payments"],
            "user_no": item["userId"],
            "banks":  [BYBIT_BANK_IDS[p] for p in item["payments"] if p in BYBIT_BANK_IDS]
        }
        for item in items
    ]

async def get_nbk_rate(currency: str = "USD") -> Optional[float]:
    url = "https://www.nationalbank.kz/rss/rates_all.xml"
    try:
        async with aiohttp.ClientSession() as session: #открыли браузер
            async with session.get(url) as response: #отправили запрос get ? 
                xml_text = await response.text()
        
        root = ET.fromstring(xml_text)

        for item in root.findall('.//item'):
            title = item.find('title').text
            if title == currency:
                rate = float(item.find('description').text) #цена
                quant = int(item.find('quant').text)
                return rate / quant #возвращает цену за 1 в тенге
        return None #если нбк не дал эту валюту, но юзеру я дам выбор строгий чтобы он не присылал нонсенс в валюте
    except Exception as e:
        print(f"Ошибка при получении курса НБК: {e}")
        return None
        
def merchant_parser(data: dict) -> list:
    return [
        {
            "price": float(m["adv"]["price"]),
            "nickname": m["advertiser"]["nickName"],
            "orders": m["advertiser"]["monthOrderCount"],
            "completion_rate": round(m["advertiser"]["monthFinishRate"] * 100, 1),
            "min_amount": float(m["adv"]["minSingleTransAmount"]),
            "max_amount": float(m["adv"]["maxSingleTransAmount"]),
            "user_no": m["advertiser"]["userNo"],
            "banks": [b["tradeMethodName"] for b in m["adv"]["tradeMethods"]],
        }
        for m in data["data"]
    ]
        


async def get_binance_p2p_rate():
    #смотрим по продавцам, seller = продавец продает, buyer = продавец покупает
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"

    try:
        payload_BUY = {
            "asset": "USDT",
            "fiat": "KZT", 
            "tradeType": "BUY",  # или "SELL"
            "page": 1,
            "rows": 10,
            "payTypes": []
            }
        
        payload_SELL = {
            "asset": "USDT",
            "fiat": "KZT", 
            "tradeType": "SELL",
            "page": 1,
            "rows": 10,
            "payTypes": []
            }
        
        async with aiohttp.ClientSession() as session: #открыли браузер
            async with session.post(url, json=payload_BUY) as response_buy:
                data_buy = await response_buy.json()

            async with session.post(url, json=payload_SELL) as response_sell:
                data_sell = await response_sell.json()

        seller_info = merchant_parser(data_buy)
        buyer_info = merchant_parser(data_sell)

        return (seller_info, buyer_info)

    
    except Exception as e:
        print(f"Ошибка: {e}")

        



async def test():
    bybit = await get_bybit_p2p_rate()
    for merchant in bybit[0]:  # покупатели
        print(f"{merchant['nickname']}: {merchant['payments']}")

