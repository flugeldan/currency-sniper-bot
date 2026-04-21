from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from models.user import User
from handlers.keyboards import keyboard, exchange_keyboard, alert_types_keyboard, alert_types_keyboard_p2p, p2p_buy_sell_choosing_keyboard, p2p_up_down_keyboard, build_banks_keyboard, banks_keyboard, listing_keyboard, swipe_sellers_buyers, swipe_alerts_keyboard, cancel_keyboard
from handlers.keyboards import AlertCallback
from services.cache import get_cache
from models.alert import PriceTargetAlert, PercentTargetAlert, P2PMerchantAlert
from services.storage import get_user, save_user
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest



from texts import merchants_page_text, show_alerts_page
import math
router = Router()
class AlertCreation(StatesGroup):
    #общие
    choosing_type = State()
    entering_zone = State()



    choosing_sell_buy_p2p = State()
    choosing_exchange = State()
    up_down = State()
    choosing_trade_type = State()

    
    entering_params = State()


    #мерчант - плайсы - продажа/покупка - мин ордера - комплишн рейт(опционально) - нужные банки
    choosing_exchange_for_merchant = State()
    choosing_sell_buy_p2p_merchant = State()
    entering_min_orders = State()
    entering_completion_rate = State()
    entering_required_banks_p2p_merchant = State()


class ListingMerchants(StatesGroup):
    choosing_exchange = State()

    swiping_pages = State()

class SwipingAlerts(StatesGroup):
    swiping_pages = State()


    

     




@router.message(F.text == "❌ Отмена")
async def cancel(message: Message, state: FSMContext):
    await state.clear()          # 4 пробела отступ
    await message.answer("Отменено", reply_markup=keyboard)


#создание уведов
async def create_price_target_alert(alert_data: dict, cache: dict, user: User):
    current_price = None
    if alert_data["exchange"] == "nbk":
        current_price = cache["nbk_price"]
        place = "nbk"
    elif alert_data["exchange"] == "binance":
        if alert_data["buy_sell"] == "sell":
            current_price = cache["binance_info"][0][0]["price"]
            place = "binance_sell"
        else:
            current_price = cache["binance_info"][1][0]["price"]
            place = "binance_buy"

    alert = PriceTargetAlert(
        user_id=user.telegram_user_id,
        active=True,
        zone_percent=alert_data["zone"],
        price_target=alert_data["price"],
        place=place,  # правильный place
        initial_price=current_price
        )

    user.alerts.append(alert)
    save_user(user)


async def create_percent_target_alert(alert_data: dict, cache: dict, user: User):
    current_price = None

    if alert_data["exchange"] == "nbk":
        current_price = cache["nbk_price"]
        place = "nbk"
    elif alert_data["exchange"] == "binance":
        if alert_data["buy_sell"] == "sell":
            current_price = cache["binance_info"][0][0]["price"]
            place = "binance_sell"
        else:
            current_price = cache["binance_info"][1][0]["price"]
            place = "binance_buy"
    


    alert = PercentTargetAlert(user_id=user.telegram_user_id,
        active=True,
        zone_percent=alert_data["zone"],
        percent_target=alert_data["percent"],
        direction=alert_data["direction"],
        place=place,  # правильный place
        initial_price=current_price)
    
    user.alerts.append(alert)

    save_user(user)

    return True

async def create_p2p_merchant_alert(alert_data: dict, cache: dict, user: dict):

    if alert_data["exchange"] == "all":
        pass 
    elif alert_data["exchange"] == "binance":
        if alert_data["buy_sell"] == "sell":
            place = "binance_sell"
        else:
            place = "binance_buy"
    elif alert_data["exchange"] == "bybit":
        if alert_data["buy_sell"] == "sell":
            place = "bybit_sell"
        else:
            place = "bybit_buy"

    alert = P2PMerchantAlert(
        user_id=user.telegram_user_id,
        active=True,
        zone_percent=None,
        minimum_completed_orders=alert_data["min_orders"],
        completion_rate=alert_data["completion_rate"],
        exchange=place,
        required_banks=alert_data["selected_banks"]
    )


    user.alerts.append(alert)
    save_user(user)
#хэндлеры


@router.message(F.text == "🎯 Мои алерты")
async def show_user_alerts(message: Message, state: FSMContext):
    await state.set_state(SwipingAlerts.swiping_pages)

    telegram_user_id = str(message.from_user.id)
    user_alerts = get_user(telegram_user_id).alerts

    if not user_alerts:
        await message.answer("У вас нету активных объявлений")
        await state.clear()
        return
    
    total_pages = math.ceil(len(user_alerts) / 5)

    await state.update_data(cur_page=0, total_pages=total_pages)


    await message.answer(show_alerts_page(user_alerts, 0, total_pages), reply_markup=swipe_alerts_keyboard(user_alerts, 0, total_pages), parse_mode="HTML")

@router.callback_query(AlertCallback.filter(F.action == "next"))
async def swipe_next_page_alerts(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = get_user(str(callback.from_user.id))
    cur_page, total_pages = data["cur_page"] + 1, data["total_pages"]

    await callback.message.edit_text(
        show_alerts_page(user.alerts, cur_page, total_pages),
        reply_markup=swipe_alerts_keyboard(user.alerts, cur_page, total_pages),
        parse_mode="HTML")

    await callback.answer()

@router.callback_query(AlertCallback.filter(F.action == "prev"))
async def swipe_next_page_alerts(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = get_user(str(callback.from_user.id))
    cur_page, total_pages = data["cur_page"] - 1, data["total_pages"]

    await callback.message.edit_text(
        show_alerts_page(user.alerts, cur_page, total_pages),
        reply_markup=swipe_alerts_keyboard(user.alerts, cur_page, total_pages),
        parse_mode="HTML")

    await callback.answer()



@router.callback_query(AlertCallback.filter(F.action == "delete_all"))
async def clear_all_alerts(callback: CallbackQuery, state: FSMContext):
    user = get_user(str(callback.from_user.id))
    user.clear_alerts()
    save_user(user)
    
    await callback.message.edit_text("🧹 Все алерты удалены")
    await state.clear()
    await callback.answer()

@router.callback_query(AlertCallback.filter(F.action == "delete"))
#коммент ниже я пишу для себя 
# AlertCallback.filter() — фильтрует callback по action
# aiogram автоматически десериализует строку "alert:delete:uuid" в объект AlertCallback
# callback_data: AlertCallback — готовый объект с атрибутами action и alert_id

async def remove_alert(callback: CallbackQuery, callback_data: AlertCallback, state: FSMContext):
    user = get_user(str(callback.from_user.id))
    alert = next((a for a in user.alerts if a.alert_id == callback_data.alert_id), None)
    if alert is None:
        await state.clear()
        await callback.answer("⚠️ Алерт уже удалён", show_alert=True)
        return
    user.remove_alert(alert)
    save_user(user)

    
    if not user.alerts:
        await state.clear()
        await callback.message.edit_text("У вас нет алертов")
        await callback.answer()
        return
    
    data = await state.get_data()
    cur_page = data["cur_page"]
    total_pages = math.ceil(len(user.alerts) / 5)
    await state.update_data(total_pages=total_pages)

    if total_pages > 0 and cur_page >= total_pages:
        cur_page = total_pages - 1
    
    await state.update_data(cur_page=cur_page, total_pages=total_pages)

    await callback.message.edit_text(
        show_alerts_page(user.alerts, cur_page, total_pages),
        reply_markup=swipe_alerts_keyboard(user.alerts, cur_page, total_pages),
        parse_mode="HTML")

    await callback.answer()

@router.callback_query(AlertCallback.filter(F.action == "toggle"))

async def toggle_alert(callback: CallbackQuery, callback_data: AlertCallback, state: FSMContext):
    user = get_user(str(callback.from_user.id))
    alert = next((a for a in user.alerts if a.alert_id == callback_data.alert_id), None)

    if alert is None:
        await state.clear()
        await callback.answer("⚠️ Алерт уже удалён", show_alert=True)
        return
    user.toggle_alert(alert.alert_id)
    save_user(user)


    
    data = await state.get_data()
    cur_page, total_pages = data["cur_page"], data["total_pages"]
    await state.update_data(cur_page=cur_page, total_pages=total_pages)
    
    await callback.message.edit_text(
        show_alerts_page(user.alerts, cur_page, total_pages),
        reply_markup=swipe_alerts_keyboard(user.alerts, cur_page, total_pages),
        parse_mode="HTML")

    await callback.answer()










@router.message(F.text == "🥇 Топ P2P мерчантов")
async def show_top_p2p_merchants(message: Message, state: FSMContext):
    await state.set_state(ListingMerchants.choosing_exchange)

    await message.answer("Выберите биржу", reply_markup=listing_keyboard)

@router.message(ListingMerchants.choosing_exchange, F.text == "📈 Binance")
async def showing_binance_merchants(message: Message, state: FSMContext):

    await state.set_state(ListingMerchants.swiping_pages)

    await state.update_data(exchange = "binance")

    cache = get_cache()
    binance_sellers = cache["binance_info"][0]
    
    await message.answer(
        merchants_page_text(binance_sellers, "binance", "sell"),
        reply_markup=swipe_sellers_buyers(0),parse_mode="HTML",
        disable_web_page_preview=True)
@router.message(ListingMerchants.choosing_exchange, F.text == "📈 Bybit")
async def showing_binance_merchants(message: Message, state: FSMContext):

    await state.set_state(ListingMerchants.swiping_pages)

    await state.update_data(exchange = "bybit")

    cache = get_cache()
    bybit_sellers = cache["bybit_info"][0]
    await message.answer(merchants_page_text(bybit_sellers, "bybit", "sell"), reply_markup=swipe_sellers_buyers(0), parse_mode="HTML", disable_web_page_preview=True)


@router.callback_query(ListingMerchants.swiping_pages, F.data == "merchants_next")
async def merchants_next_page(callback: CallbackQuery, state: FSMContext):
    page_info = await state.get_data()
    cache = get_cache()

    if page_info["exchange"] == "binance":
        binance_buyers = cache["binance_info"][1]
        
        await callback.message.edit_text(merchants_page_text(binance_buyers,"binance", "buy"), reply_markup=swipe_sellers_buyers(1), parse_mode="HTML", disable_web_page_preview=True)

    elif page_info["exchange"] == "bybit":

        bybit_buyers = cache["bybit_info"][1]

        await callback.message.edit_text(merchants_page_text(bybit_buyers,"bybit", "buy"), reply_markup=swipe_sellers_buyers(1), parse_mode="HTML", disable_web_page_preview=True)

    await callback.answer()


@router.callback_query(ListingMerchants.swiping_pages, F.data == "merchants_prev")
async def merchants_prev_page(callback: CallbackQuery, state: FSMContext):
    page_info = await state.get_data()
    cache = get_cache()

    if page_info["exchange"] == "binance":
        binance_buyers = cache["binance_info"][0]
        
        await callback.message.edit_text(merchants_page_text(binance_buyers, "binance", "sell"), reply_markup=swipe_sellers_buyers(0), parse_mode="HTML", disable_web_page_preview=True)

    elif page_info["exchange"] == "bybit":

        bybit_buyers = cache["bybit_info"][0]

        await callback.message.edit_text(merchants_page_text(bybit_buyers,"bybit", "sell"), reply_markup=swipe_sellers_buyers(0), parse_mode="HTML", disable_web_page_preview=True)

    await callback.answer()





    

    
















@router.message(F.text == "💵 Курс доллара (НБК)")
async def start_price_alert_nbk(message: Message, state: FSMContext):
    # 1. сохрани тип алерта в state
    await state.update_data(alert_type = "price_target")

    await state.update_data(exchange = "nbk")
    # 2. переведи в состояние choosing_place
    await state.set_state(AlertCreation.entering_params)

    # 3. спроси у пользователя цену
    await message.answer("Введите желаемую цену/процент ", reply_markup=keyboard)


@router.message(F.text == "📊 P2P ордера")
async def start_p2p_alert_creation(message: Message, state: FSMContext):
    await message.answer("Введите тип уведомления: ", reply_markup=alert_types_keyboard_p2p)

    await state.set_state(AlertCreation.choosing_type)


@router.message(AlertCreation.choosing_type, F.text == "Цена по P2P ордерам 💸")
async def p2p_alert_price_target(message: Message, state: FSMContext):
    #ставим тип и спрашиваем площадку, обновляем дату в словаре
    await state.update_data(alert_type = "price_target")
    await state.set_state(AlertCreation.choosing_exchange)
    await message.answer("Выберите площадку: ", reply_markup=exchange_keyboard)

@router.message(AlertCreation.choosing_type, F.text == "Изменение в процентах %")
async def p2p_alert_percent_target(message: Message, state: FSMContext):

    await state.update_data(alert_type = "percent_target")

    await state.set_state(AlertCreation.up_down)

    await message.answer("Рост/падение: ↕️ ", reply_markup=p2p_up_down_keyboard)



@router.message(AlertCreation.up_down, F.text == "Рост ⬆️")
async def p2p_up(message: Message, state: FSMContext):
    await state.update_data(direction = "up")

    await state.set_state(AlertCreation.choosing_exchange)

    await message.answer("Выберите плошадку:", reply_markup=exchange_keyboard)


@router.message(AlertCreation.up_down, F.text == "Падение ⬇️")
async def p2p_down(message: Message, state: FSMContext):
    await state.update_data(direction = "down")

    await state.set_state(AlertCreation.choosing_exchange)

    await message.answer("Выберите плошадку:", reply_markup=exchange_keyboard)


@router.message(AlertCreation.choosing_exchange, F.text == "📈 Binance")
async def chosing_p2p_type_binance(message: Message, state: FSMContext):
    await state.update_data(exchange = "binance")

    await state.set_state(AlertCreation.choosing_sell_buy_p2p)

    await message.answer("Введите тип объявления продажа/покупка: ", reply_markup=p2p_buy_sell_choosing_keyboard)

@router.message(AlertCreation.choosing_exchange, F.text == "📈 Binance")
async def chosing_p2p_type_bybit(message: Message, state: FSMContext):
    await state.update_data(exchange = "bybit")

    await state.set_state(AlertCreation.choosing_sell_buy_p2p)

    await message.answer("Введите тип объявления продажа/покупка: ", reply_markup=p2p_buy_sell_choosing_keyboard)

@router.message(AlertCreation.choosing_sell_buy_p2p, F.text == "Продажа 💲")
async def p2p_type_sell(message: Message, state: FSMContext):
    await state.update_data(buy_sell = "sell")

    await state.set_state(AlertCreation.entering_params)

    await message.answer("Введите желаемую цену/процент: ")

@router.message(AlertCreation.choosing_sell_buy_p2p, F.text == "Покупка 🛒")
async def p2p_type_buy(message: Message, state: FSMContext):
    await state.update_data(buy_sell = "buy")

    await state.set_state(AlertCreation.entering_params)

    await message.answer("Введите желаемую цену/процент: ", reply_markup=cancel_keyboard)


@router.message(AlertCreation.entering_params)
async def entering_price(message: Message, state: FSMContext):
    alert_info = await state.get_data()
    try:
        goal_number = float(message.text)
    except ValueError:
        await message.answer("❌ Введите число, например: 490.5")
        return
    
    if alert_info["alert_type"] == "price_target":
        await state.update_data(price=goal_number)

    elif alert_info["alert_type"] == "percent_target":
        await state.update_data(percent=goal_number)


    await state.set_state(AlertCreation.entering_zone)
    await message.answer("Введите зону защиты в % (например 1.5):")














@router.message(F.text == "👤 P2P мерчанты")
async def start_p2p_merchants_alert(message: Message, state: FSMContext):
    await state.update_data(alert_type="p2p_merchant")

    await state.update_data(user_id = str(message.from_user.id))

    await state.set_state(AlertCreation.choosing_exchange_for_merchant)
    
    await message.answer("Выберите биржу", reply_markup=exchange_keyboard)

@router.message(AlertCreation.choosing_exchange_for_merchant, F.text == "📈 Binance")
#надо будет добавить хэндлер специально для all в будущем
async def choosing_exchange_p2p_merchant_binance(message: Message, state: FSMContext):
    await state.update_data(exchange="binance")

    await state.set_state(AlertCreation.choosing_sell_buy_p2p_merchant)
    
    await message.answer("Мерчант должен продавать/покупать: ", reply_markup=p2p_buy_sell_choosing_keyboard)

@router.message(AlertCreation.choosing_exchange_for_merchant, F.text == "📈 Bybit")
async def choosing_exchange_p2p_bybit(message: Message, state: FSMContext):
    await state.update_data(exchange="bybit")

    await state.set_state(AlertCreation.choosing_sell_buy_p2p_merchant)
    
    await message.answer("Мерчант должен продавать/покупать: ", reply_markup=p2p_buy_sell_choosing_keyboard)



@router.message(AlertCreation.choosing_sell_buy_p2p_merchant, F.text == "Продажа 💲")
async def p2p_merchant_sell(message: Message, state: FSMContext):

    await state.update_data(buy_sell = "sell")

    await state.set_state(AlertCreation.entering_min_orders)

    await message.answer("Введите минимальное количество ордеров: ")


@router.message(AlertCreation.choosing_sell_buy_p2p_merchant, F.text == "Покупка 🛒")
async def p2p_merchant_buy(message: Message, state: FSMContext):

    await state.update_data(buy_sell = "buy")

    await state.set_state(AlertCreation.entering_min_orders)

    await message.answer("Введите минимальное количество ордеров: ")

@router.message(AlertCreation.entering_min_orders)
async def p2p_merchant_entering_min_orders(message: Message, state: FSMContext):

    try:
        min_orders = int(message.text)
    except ValueError:
        await message.answer("❌ Введите число, например: 100")
        return
    
    await state.update_data(min_orders = min_orders)
    
    await state.set_state(AlertCreation.entering_completion_rate)

    await message.answer("Введите минимальный рейтинг успеха мерчанта: ")

@router.message(AlertCreation.entering_completion_rate)
async def p2p_merchant_completion_rate(message: Message, state: FSMContext):

    try:
        completion_rate = float(message.text)
        if completion_rate < 0 or completion_rate > 100:
            await message.answer("❌ Вводите число в пределах 0-100")
            return
    except ValueError:
        await message.answer("❌ Введите нужный процент, например 99.9")
        return

    
    await state.update_data(completion_rate=completion_rate)

    await state.set_state(AlertCreation.entering_required_banks_p2p_merchant)

    await message.answer("Выберите нужные банки: ", reply_markup=build_banks_keyboard(set()))






@router.callback_query(
    AlertCreation.entering_required_banks_p2p_merchant,
    F.data.startswith("bank_")
)
async def toggle_bank(callback: CallbackQuery, state: FSMContext):
    bank_key = callback.data.removeprefix("bank_")

    data = await state.get_data()

    selected = set(data.get("selected_banks", []))

    if bank_key in selected:
        selected.remove(bank_key)
    else:
        selected.add(bank_key)

    await state.update_data(selected_banks = list(selected))
    try:
        await callback.message.edit_reply_markup(reply_markup = build_banks_keyboard(selected))
    except TelegramBadRequest:
        pass

    await callback.answer()
    



@router.callback_query(
    AlertCreation.entering_required_banks_p2p_merchant,
    F.data == "banks_next")
async def banks_next(callback: CallbackQuery, state: FSMContext):

    alert_data = await state.get_data()
    cache = get_cache()
    user = get_user(alert_data["user_id"])

    if not alert_data.get("selected_banks", []):
        await callback.answer("⚠️ Выбери хотя бы один банк!", show_alert=True)
        return

    try:
        await create_p2p_merchant_alert(alert_data, cache, user)
    
    except ValueError as e:
        await state.clear()
        await callback.message.answer(f"❌ {e}. Попробуйте позже.", reply_markup=keyboard)
        return

    await state.clear()
    await callback.message.answer("✅ Алерт создан!", reply_markup=keyboard)

    await callback.answer()




@router.callback_query(
    AlertCreation.entering_required_banks_p2p_merchant,
    F.data == "banks_cancel"
)
async def banks_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    await callback.message.edit_text("Отменено")

    await callback.message.answer("Главное меню", reply_markup=keyboard)

    await callback.answer()












@router.message(AlertCreation.entering_zone)
async def enter_zone(message: Message, state: FSMContext):

    try:
        zone = float(message.text)
    except ValueError:
        await message.answer("❌ Введите число, например: 490.5")
        return
    
    await state.update_data(zone = zone)

    alert_info = await state.get_data()
    cache = get_cache()

    user = get_user(str(message.from_user.id))

        
    
    try:
        if alert_info["alert_type"] == "price_target":
            await create_price_target_alert(alert_info, cache, user)
        else:
            await create_percent_target_alert(alert_info, cache, user)
    except ValueError as e:
        await state.clear()
        await message.answer(f"❌ {e}. Попробуйте позже.", reply_markup=keyboard)
        return

    await state.clear()
    await message.answer("✅ Алерт создан!", reply_markup=keyboard)










