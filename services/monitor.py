import asyncio
from aiogram import Bot
from services.fetcher import get_nbk_rate, get_binance_p2p_rate, get_bybit_p2p_rate
from repository.user_repository import UserRepository
from models.alert import PriceTargetAlert, PercentTargetAlert, ArbitrageAlert, SpreadAlert, P2PMerchantAlert
from services.analyzer import (calculate_arbitrage, filter_best_merchants, 
                                check_price_target, check_percent_target, is_outside_zone, is_cooldown_passed, is_outside_zone_by_spread)
from datetime import datetime, timedelta
from services.cache import update_cache, get_cache
from services.logger import get_logger
logger = get_logger(__name__)

async def check_price_target_alert(alert, prices, bot) -> bool:
    current_price = prices.get(alert.place)
    if current_price is None:
        return False
    if not is_outside_zone(current_price, alert.last_triggered_price, alert.zone_percent):
        return False
    if check_price_target(current_price, alert.price_target, alert.direction):
        await bot.send_message(alert.user_id, 
                               f"🎯 Алерт сработал!\n"
                               f"Курс достиг {alert.price_target}\n"
                               f"Текущий курс: {current_price}")
        alert.last_triggered_price = current_price
        return True
    return False

async def check_percent_target_alert(alert, prices, bot) -> bool:
    current_price = prices.get(alert.place)
    if not is_outside_zone(current_price, alert.last_triggered_price, alert.zone_percent):
        return False
    if check_percent_target(current_price,alert.initial_price, alert.percent_target, alert.direction):
        await bot.send_message(alert.user_id, 
                               f"🎯 Алерт сработал!\n"
                               f"Курс достиг {alert.price_target}\n"
                               f"Текущий курс: {current_price}")
        alert.last_triggered_price = current_price
        return True
    return False

async def check_P2P_merchant_alert(alert, prices, binance_info, bybit_info, bot):
    if alert.exchange == "binance":
        if alert.buy_sell == "sell":
            merchants_data = binance_info[0]
        else:
            merchants_data = binance_info[1]
    elif alert.exchange == "bybit":
        if bybit_info is None:
            return False
        if alert.buy_sell == "sell":
            merchants_data = bybit_info[0]
        else:
            merchants_data = bybit_info[1]
    else:
        return False
    
    if is_cooldown_passed(alert.last_triggered_at, 30):
        banks = set(alert.required_banks) if alert.required_banks else None
        compatible_merchants = filter_best_merchants(merchants_data, alert.completion_rate, 
                                             alert.minimum_completed_orders, banks)
        if not compatible_merchants:
            return False
        
        for merchant in compatible_merchants:
                banks_str = ", ".join(merchant['banks'])
                if alert.exchange == "binance":
                    link = f"https://p2p.binance.com/en/advertiserDetail?advertiserNo={merchant['user_no']}"
                elif alert.exchange == "bybit":
                    link = f"https://www.bybit.com/en/p2p/order?userId={merchant['user_no']}"
                await bot.send_message(

                    alert.user_id,
                    f"👤 Мерчант найден!\n"
                    f"Ник: {merchant['nickname']}\n"
                    f"Цена: {merchant['price']} KZT\n"
                    f"Сделок: {merchant['orders']} | "
                    f"Completion: {merchant['completion_rate']:.1f}%\n"
                    f"Банки: {banks_str}\n"
                    f"{link}")
        alert.last_triggered_at = datetime.now().isoformat()
        return True
    else:
        return False
    
async def check_arbitrage_alert(alert, prices, binance_info, current_nbk_price, bot):

    spread_calc = {
        "nbk_vs_sell": lambda: (prices["nbk"] - prices["binance_sell"], prices["nbk"]), #spread and its percent
        "nbk_vs_buy": lambda: (prices["binance_buy"] - prices["nbk"],prices["binance_buy"]),
        "sell_vs_buy": lambda: (prices["binance_buy"] - prices["binance_sell"], prices["binance_buy"]),
        "buy_vs_sell": lambda: (prices["binance_sell"] - prices["binance_buy"], prices["binance_buy"])
        }
    calc = spread_calc.get(alert.arb_type, None)
    if not calc:
        return False
    
    current_spread, current_price = calc()
    
    if current_spread >= alert.goal_spread:
        if is_outside_zone_by_spread(current_price, alert.last_triggered_spread_price, alert.last_triggered_spread):
            await bot.send_message(
                alert.user_id,
                f"💰 Арбитражная возможность!\n"
                f"Спред: {current_spread:.2f} KZT\n"
                f"Цель была: {alert.goal_spread} KZT"
                )
            alert.last_triggered_spread = current_spread
            alert.last_triggered_spread_price = current_price
            return True
        
    return False
    
async def monitor_loop(bot: Bot, repo: UserRepository):
    while True:
        try:
            # 1. получаем данные
            binance_info = await get_binance_p2p_rate()
            bybit_info = await get_bybit_p2p_rate()
            current_nbk_price = await get_nbk_rate("USD")

            update_cache(current_nbk_price, binance_info, bybit_info)
            if binance_info is None and current_nbk_price is None and bybit_info is None:
                 logger.error(f"Ошибка монитора: {e}", exc_info=True)
                 await asyncio.sleep(60)
                 continue
            
            prices = {}
            users = await repo.get_all_users()

            if current_nbk_price:
                prices["nbk"] = current_nbk_price
            if binance_info:
                 prices["binance_sell"] = float(binance_info[0][0]['price'])
                 prices["binance_buy"] = float(binance_info[1][0]['price'])
            if bybit_info:
                 prices["bybit_sell"] = float(bybit_info[0][0]['price'])
                 prices["bybit_buy"] = float(bybit_info[1][0]['price'])

            
            
            # 3. проверяем алерты
            for user in users:
                user_alers =  user.alerts
                user_changed = False

                for alert in user_alers:
                    if alert.active == False:
                        continue
                    if isinstance(alert, PriceTargetAlert):
                      changed = await check_price_target_alert(alert, prices, bot)

                    elif isinstance(alert, PercentTargetAlert):
                        changed = await check_percent_target_alert(alert, prices, bot)
                    
                    elif isinstance(alert, P2PMerchantAlert):
                        changed = await check_P2P_merchant_alert(alert, prices, binance_info, bybit_info, bot)
                    
                    elif isinstance(alert, ArbitrageAlert):
                        changed = await check_arbitrage_alert(alert, prices, binance_info, current_nbk_price, bot)

                    
                    elif isinstance(alert, SpreadAlert):
                        changed = False
                        pass
                    
                    else:
                        changed = False

                    if changed == True:
                        await repo.save_alert(alert)
                    #переделал в моменте арбитраж алерт, из за этого спред алерт чуть бесполезен, наверное сделаю из него чисто сборщик спредов между криптобиржами, или реальными обменниками/нбк?

                
                        
        except Exception as e:
            logger.error(f"Ошибка монитора: {e}", exc_info=True)
        
        await asyncio.sleep(60)