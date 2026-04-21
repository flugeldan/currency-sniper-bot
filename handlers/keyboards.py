# handlers/keyboards.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery
from aiogram.filters.callback_data import CallbackData
class AlertCallback(CallbackData, prefix="alert"):
    action: str # delete, delete_all, toggle
    alert_id: str

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 Текущие курсы"), KeyboardButton(text="🎯 Мои алерты")],
        [KeyboardButton(text="➕ Создать алерт")],
        [KeyboardButton(text="🥇 Топ P2P мерчантов"), KeyboardButton(text="🔍 Как пользоваться")],
    ],
    resize_keyboard=True
)

exchange_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📈 Binance")],
        [KeyboardButton(text="📈 Bybit")],
        [KeyboardButton(text="❌ Отмена")]


    ],
    resize_keyboard=True
)



alert_types_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💵 Курс доллара (НБК)"), KeyboardButton(text="📊 P2P ордера")],
        [KeyboardButton(text="👤 P2P мерчанты"), KeyboardButton(text="📈 Арбитраж (в разработке)")],
        [KeyboardButton(text="❌ Отмена")]
    ],
    resize_keyboard=True
)
cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="❌ Отмена")]
    ],
    resize_keyboard=True)

alert_types_keyboard_p2p = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Изменение в процентах %"), KeyboardButton(text="Цена по P2P ордерам 💸")],
    ],
    resize_keyboard=True
)

p2p_buy_sell_choosing_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Продажа 💲"), KeyboardButton(text="Покупка 🛒")],
    ],
    resize_keyboard=True
)

p2p_up_down_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Рост ⬆️"), KeyboardButton(text="Падение ⬇️")],
    ],
    resize_keyboard=True
)

listing_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📈 Binance")],
        [KeyboardButton(text="📈 Bybit")],
        [KeyboardButton(text="❌ Отмена")]


    ],
    resize_keyboard=True
)


banks_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Kaspi", callback_data="bank_kaspi"),
            InlineKeyboardButton(text="Freedom", callback_data="bank_freedom"),
            InlineKeyboardButton(text="Halyk", callback_data="bank_halyk"),
        ],
        [
            InlineKeyboardButton(text="Дальше ➡️", callback_data="banks_next"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="banks_cancel"),
        ]
    ]
)

BANKS = [("Kaspi", "kaspi"), ("Freedom", "freedom"), ("Halyk", "halyk")]

def build_banks_keyboard(selected: set) -> InlineKeyboardMarkup:
    buttons = []

    for name, key in BANKS:
        text = f"✅ {name}" if key in selected else name
        buttons.append(InlineKeyboardButton(text = text, callback_data=f"bank_{key}"))

    return InlineKeyboardMarkup(inline_keyboard=[buttons, [
            InlineKeyboardButton(text="Дальше ➡️", callback_data="banks_next"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="banks_cancel"),
        ]
    ])

def swipe_sellers_buyers(current_page: int):
    buttons = []

    if current_page == 0:
        buttons.append(InlineKeyboardButton(text = "➡️", callback_data="merchants_next"))
    else:
        buttons.append(InlineKeyboardButton(text="◀️", callback_data="merchants_prev"))
    
    return InlineKeyboardMarkup(inline_keyboard=[buttons])

def swipe_alerts_keyboard(alerts: list, current_page: int, total_pages: int):
    page_first_alert_index = current_page * 5
    alert_page = alerts[page_first_alert_index:page_first_alert_index + 5]
    nav_buttons, delete_buttons = [], []
    toggle_buttons = []
    for i, alert in enumerate(alert_page, page_first_alert_index + 1):
        icon = "🔔" if alert.active else "🔕"
        toggle_buttons.append(InlineKeyboardButton(text=f"{icon} {i}", callback_data=AlertCallback(action="toggle", alert_id=alert.alert_id).pack()))
        delete_buttons.append(InlineKeyboardButton(text=f"🗑 {i}", callback_data=AlertCallback(action="delete", alert_id=alert.alert_id).pack()))



    if current_page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(text="➡️", callback_data=AlertCallback(action="next", alert_id="none").pack()))
    
    if current_page > 0:
        nav_buttons.append(InlineKeyboardButton(text="◀️", callback_data=AlertCallback(action="prev", alert_id="none").pack()))


    rows = [nav_buttons, toggle_buttons, delete_buttons] if nav_buttons else [toggle_buttons,delete_buttons]
    rows.append([InlineKeyboardButton(text="🧹 Очистить все", callback_data=AlertCallback(action="delete_all", alert_id="all").pack())])
    
    


    return InlineKeyboardMarkup(inline_keyboard=rows)





    







    