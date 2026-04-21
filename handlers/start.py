from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from aiogram import F, Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from services.storage import get_user
from services.fetcher import get_nbk_rate, get_binance_p2p_rate
from services.analyzer import calculate_arbitrage
from services.cache import get_cache
from texts import WELCOME, LOADING, rates_message, list_top_merchants, split_pages, merchants_page_text
from aiogram.types import CallbackQuery
from models.alert import PriceTargetAlert, PercentTargetAlert, ArbitrageAlert, SpreadAlert, P2PMerchantAlert
from handlers.alerts import AlertCreation, cancel
from handlers.keyboards import keyboard, exchange_keyboard, alert_types_keyboard
from aiogram.fsm.context import FSMContext
from texts import FAQ_TEXT
router = Router()



@router.message(CommandStart())
async def cmd_start(message: Message):
    get_user(str(message.from_user.id), message.from_user.username or "")
    await message.answer("Здравствуй, я телеграм бот по снайпу выгодных спредов валют", reply_markup=keyboard)


@router.message(F.text == "📊 Текущие курсы")
async def current_rates(message: Message):
    await message.answer(LOADING)
    data = get_cache()
    nbk_price = data["nbk_price"]
    binance_info = data["binance_info"]
    bybit_info = data["bybit_info"]

    if nbk_price is None or binance_info is None:
        await message.answer("⏳ Данные ещё загружаются, подождите минуту...")
        return

    p2p_info_binance = calculate_arbitrage(nbk_price, binance_info, "binance")
    p2p_info_bybit = calculate_arbitrage(nbk_price, bybit_info, "bybit") if bybit_info else None

    await message.answer(
        rates_message(nbk_price, binance_info, bybit_info, p2p_info_binance, p2p_info_bybit),
        parse_mode="HTML",
        disable_web_page_preview=True
    )
def merchant_keyboard(page: int, total_pages: int, exchange: str, trade_type: str):
    buttons = []
    
    if page > 0:  # если не первая страница
        buttons.append(InlineKeyboardButton(
            text="◀️", 
            callback_data=f"merchant_{exchange}_{trade_type}_{page-1}"
        ))

    if page < total_pages - 1: #если не послденаяя, логика без ==1, ==2 чтобы в будущем можно было больше страниц добавлять, смотрим по первой и последней
        buttons.append(InlineKeyboardButton(text= "▶️", callback_data=f'merchant_{exchange}_{trade_type}_{page+1}')) 
    buttons.append(InlineKeyboardButton(text=f'{page + 1} / {total_pages}', callback_data="noop"))

    return InlineKeyboardMarkup(inline_keyboard=[buttons])


@router.message(F.text == "🥇 Топ P2P мерчантов")
async def top_merchants(message: Message):
    await message.answer(LOADING)
    data = get_cache()
    nbk_price = data["nbk_price"]
    binance_info = data["binance_info"]

    if nbk_price is None or binance_info is None:
        await message.answer("⏳ Данные ещё загружаются, подождите минуту...")
        return
    sellers_pages = split_pages(binance_info[0])
    buyers_pages = split_pages(binance_info[1])

    await message.answer(
        merchants_page_text(sellers_pages[0], "sell"),
        reply_markup=merchant_keyboard(0, len(sellers_pages), "binance", "sell"),
        parse_mode="HTML"
        )
    await message.answer(
        merchants_page_text(buyers_pages[0], "buy"),
        reply_markup=merchant_keyboard(0, len(buyers_pages), "binance", "buy"),
        parse_mode="HTML")
        
    
@router.callback_query(F.data.startswith("merchant_"))
async def paginate_merchant(callback: CallbackQuery):
    data = get_cache()
    if data["binance_info"] is None:
        await callback.answer("⏳ Данные ещё загружаются, подождите минуту...")
        return
    _, exchange, trade_type, page = callback.data.split("_")
    page = int(page)
    merchants = data["binance_info"][0] if trade_type == "sell" else data["binance_info"][1]
    pages = split_pages(merchants)
    
    await callback.message.edit_text(merchants_page_text(pages[page], trade_type), reply_markup=merchant_keyboard(page, len(pages), exchange, trade_type), parse_mode='HTML')
    await callback.answer()


@router.message(F.text == "➕ Создать алерт")
async def alert_creation(message: Message, state: FSMContext):
    await state.set_state(AlertCreation.choosing_type)

    await message.answer("Выберите тип уведомления 🔔", reply_markup=alert_types_keyboard)

@router.message(F.text == "🔍 Как пользоваться")
async def faq(message: Message):
    await message.answer(FAQ_TEXT, parse_mode='HTML')






    
    
    
    

