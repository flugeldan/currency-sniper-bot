# texts.py

from models.alert import PriceTargetAlert, PercentTargetAlert, P2PMerchantAlert

WELCOME = "👋 Здравствуй! Я бот-снайпер курсов валют и P2P спредов.\n\nВыбери действие:"

LOADING = "⏳ Загружаю данные..."
def rates_message(nbk_price: float, binance_info: tuple, bybit_info, p2p_info_binance, p2p_info_bybit):
    best_seller_b = p2p_info_binance['best_seller']
    best_buyer_b = p2p_info_binance['best_buyer']

    text = (
        f"<b>📊 Текущие курсы</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🏦 НБК: <code>{nbk_price:.2f}</code> KZT\n\n"
        f"<b>Binance 📈</b>\n"
        f"📤 Продавец: {best_seller_b['nickname']} · ✅ {best_seller_b['completion_rate']:.0f}% · 💰 {best_seller_b['price']:.2f} KZT\n"
        f"📥 Покупатель: {best_buyer_b['nickname']} · ✅ {best_buyer_b['completion_rate']:.0f}% · 💰 {best_buyer_b['price']:.2f} KZT\n\n"
        f"<b>Спреды Binance</b>\n"
        f"├ НБК → лучший продавец: {p2p_info_binance['best_spread_sellers_price']:.2f} KZT ({p2p_info_binance['best_spread_seller_percent']:.2f}%)\n"
        f"├ НБК → средний продавец: {p2p_info_binance['avg_spread_sellers']:.2f} KZT ({p2p_info_binance['avg_spread_sellers_percent']:.2f}%)\n"
        f"├ НБК → лучший покупатель: {p2p_info_binance['best_spread_buyers_price']:.2f} KZT ({p2p_info_binance['best_spread_buyers_percent']:.2f}%)\n"
        f"├ НБК → средний покупатель: {p2p_info_binance['avg_spread_buyers']:.2f} KZT ({p2p_info_binance['avg_spread_buyers_percent']:.2f}%)\n"
        f"└ Продавец/Покупатель: {p2p_info_binance['buy_sell_spread']:.2f} KZT ({p2p_info_binance['buy_sell_spread_percent']:.2f}%)\n"
    )

    if bybit_info and p2p_info_bybit:
        best_seller_y = p2p_info_bybit['best_seller']
        best_buyer_y = p2p_info_bybit['best_buyer']

        avg_bin_sell_byb_buy = sum(s['price'] - b['price'] for s in binance_info[0] for b in bybit_info[1]) / (len(binance_info[0]) * len(bybit_info[1]))
        avg_byb_sell_bin_buy = sum(s['price'] - b['price'] for s in bybit_info[0] for b in binance_info[1]) / (len(bybit_info[0]) * len(binance_info[1]))

        text += (
            f"\n<b>Bybit 📈</b>\n"
            f"📤 Продавец: {best_seller_y['nickname']} · ✅ {best_seller_y['completion_rate']:.0f}% · 💰 {best_seller_y['price']:.2f} KZT\n"
            f"📥 Покупатель: {best_buyer_y['nickname']} · ✅ {best_buyer_y['completion_rate']:.0f}% · 💰 {best_buyer_y['price']:.2f} KZT\n\n"
            f"<b>Спреды Bybit</b>\n"
            f"├ НБК → лучший продавец: {p2p_info_bybit['best_spread_sellers_price']:.2f} KZT ({p2p_info_bybit['best_spread_seller_percent']:.2f}%)\n"
            f"├ НБК → средний продавец: {p2p_info_bybit['avg_spread_sellers']:.2f} KZT ({p2p_info_bybit['avg_spread_sellers_percent']:.2f}%)\n"
            f"├ НБК → лучший покупатель: {p2p_info_bybit['best_spread_buyers_price']:.2f} KZT ({p2p_info_bybit['best_spread_buyers_percent']:.2f}%)\n"
            f"├ НБК → средний покупатель: {p2p_info_bybit['avg_spread_buyers']:.2f} KZT ({p2p_info_bybit['avg_spread_buyers_percent']:.2f}%)\n"
            f"└ Продавец/Покупатель: {p2p_info_bybit['buy_sell_spread']:.2f} KZT ({p2p_info_bybit['buy_sell_spread_percent']:.2f}%)\n\n"
            f"<b>Арбитраж между биржами 💱</b>\n"
            f"├ Binance продавец → Bybit покупатель: {best_seller_b['price'] - best_buyer_y['price']:.2f} KZT (лучший)\n"
            f"├ Средний Binance/Bybit: {avg_bin_sell_byb_buy:.2f} KZT\n"
            f"├ Bybit продавец → Binance покупатель: {best_seller_y['price'] - best_buyer_b['price']:.2f} KZT (лучший)\n"
            f"└ Средний Bybit/Binance: {avg_byb_sell_bin_buy:.2f} KZT\n"
        )

    return text






    return text


def list_top_merchants(merchants):
    sellers, buyers = merchants[0], merchants[1]
    sellers_string = "📈 <b>Топ продавцов (купить USDT)</b>\n\n"
    buyers_string = "📉 <b>Топ покупателей (продать USDT)</b>\n\n"
    
    for seller in sellers:
        link = f'<a href="https://p2p.binance.com/en/advertiserDetail?advertiserNo={seller["user_no"]}">{seller["nickname"]}</a>'
        first_line = f"{link} ({seller['positiveRate']*100:.1f}% ✅)\n"
        second_line = f"{seller['price']:.2f} KZT\n\n"
        sellers_string += first_line + second_line
    
    for buyer in buyers:
        link = f'<a href="https://p2p.binance.com/en/advertiserDetail?advertiserNo={buyer["user_no"]}">{buyer["nickname"]}</a>'
        first_line = f"{link} ({buyer['positiveRate']*100:.1f}% ✅)\n"
        second_line = f"{buyer['price']:.2f} KZT\n\n"
        buyers_string += first_line + second_line
    
    return (sellers_string, buyers_string)


def split_pages(merchants: list, page_size: int = 5) -> list:
    # [[0,1,2,3,4], [5,6,7,8,9]] — список страниц
    return [merchants[i:i + page_size] for i in range(0, len(merchants), page_size)]



def merchants_page_text(merchants_page: list, exchange: str, trade_type: str) -> str:
    header = "📈 <b>Топ продавцов</b>\n\n" if trade_type == "sell" else "📉 <b>Топ покупателей</b>\n\n"
    text = header
    for i, m in enumerate(merchants_page, 1):
        if exchange == "binance":
            link = f'<a href="https://p2p.binance.com/en/advertiserDetail?advertiserNo={m["user_no"]}">{m["nickname"]}</a>'
        elif exchange == "bybit":
            link = f'<a href="https://www.bybit.com/en/p2p/order?userId={m["user_no"]}">{m["nickname"]}</a>'
        banks = ', '.join(m['banks'])
        text += f"{i}. {link} · ✅ {m['completion_rate']:.0f}% · 💰 {m['price']:.2f} KZT\n"
        text += f"🏦 {banks}\n\n"
    return text


def show_alerts_page(alerts: list, cur_page: int, total_pages: int) -> str:
    start = cur_page * 5
    page_alerts = alerts[start:start + 5]
    
    text = f"🎯 <b>Мои алерты</b> ({cur_page + 1}/{total_pages})\n"
    text += "━━━━━━━━━━━━━━━\n\n"
    
    for i, alert in enumerate(page_alerts, start + 1):
        if alert.__class__.__name__ == "PriceTargetAlert":
            text += f"{i}. 💵 {alert.place.upper()} → {alert.price_target} KZT · зона {alert.zone_percent}%\n"
        elif alert.__class__.__name__ == "PercentTargetAlert":
            direction = "⬆️" if alert.direction == "up" else "⬇️"
            text += f"{i}. 📊 {alert.place.upper()} {direction} {alert.percent_target}% · зона {alert.zone_percent}%\n"
        elif alert.__class__.__name__ == "P2PMerchantAlert":
            banks = ", ".join(alert.required_banks) if alert.required_banks else "любой"
            text += f"{i}. 👤 Мерчант {alert.exchange} · {banks}\n"
    
    return text









FAQ_TEXT = """
<b>🔍 Как пользоваться ботом</b>
━━━━━━━━━━━━━━━

<b>📊 Текущие курсы</b>
Показывает актуальные P2P курсы с Binance и Bybit, спреды от НБК и арбитражные возможности между биржами. Данные обновляются каждую минуту.

<b>🥇 Топ P2P мерчантов</b>
Список 10 лучших мерчантов по цене на Binance или Bybit. Можно переключаться между продавцами и покупателями. Ник каждого мерчанта — кликабельная ссылка на его профиль.

<b>🎯 Мои алерты</b>
Список всех твоих уведомлений с пагинацией по 5 штук.
├ 🔔/🔕 — включить или выключить алерт без удаления
├ 🗑 1..5 — удалить конкретный алерт по номеру
└ 🧹 Очистить все — удалить все алерты сразу

<b>➕ Создать алерт</b>
Бот пришлёт уведомление когда:
├ 💵 <b>Курс НБК</b> достигнет нужной цены
├ 📊 <b>P2P цена</b> достигнет нужного уровня или изменится на заданный %
└ 👤 <b>P2P мерчант</b> появится с нужными параметрами (банк, кол-во сделок, рейтинг)

<b>⚙️ Зона защиты</b>
При создании алерта бот просит ввести зону защиты в %. Это защита от повторных уведомлений — бот не будет спамить пока цена не отойдёт от точки срабатывания на указанный процент.

━━━━━━━━━━━━━━━
💡 По вопросам и предложениям: @reidalreadytaken
"""

