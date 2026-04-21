import json
from models.user import User
from models.alert import Alert, PriceTargetAlert, PercentTargetAlert, ArbitrageAlert, SpreadAlert, P2PMerchantAlert
from pathlib import Path
import os

DATA_FILE = "data/users.json"

os.makedirs("data", exist_ok=True)

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump({}, f)



def dict_to_alert(data: dict):
    #из словаря жсон обратно в объект алерта
    if data['type'] == 'PriceTargetAlert':
        alert = PriceTargetAlert(data['user_id'], data['active'], data['zone_percent'], data['price_target'], data['place'], 0.0)
        alert.direction = data['direction']

    elif data['type'] == 'PercentTargetAlert':
         
         alert = PercentTargetAlert(data['user_id'], data['active'], data['zone_percent'], 
                               data['direction'], data['percent_target'], data['place'],
                               data.get('initial_price', 0.0))
         
         

    elif data['type'] == 'P2PMerchantAlert':
        alert = P2PMerchantAlert(data['user_id'], data['active'], data['zone_percent'],  data['minimum_completed_orders'], data['completion_rate'], data['exchange'], data['required_banks'], data['arb_type'])
        
    
    elif data['type'] == 'ArbitrageAlert':
        alert = ArbitrageAlert(data['user_id'], data['active'], data['zone_percent'],  data['goal_spread'], data['last_triggered_spread'], data['last_triggered_spread_price'])
    
    elif data['type'] == 'SpreadAlert':
        alert = SpreadAlert(data['user_id'], data['active'], data['zone_percent'], data['goal_spread'], data['bank'], data['exchange_place'])

    else:
        raise ValueError(f"Неизвестный тип алерта: {data['type']}")
    alert.alert_id = data['alert_id']
    alert.created_at = data['created_at']
    alert.last_triggered_price = data.get('last_triggered_price', None)
    alert.last_triggered_at = data.get('last_triggered_at', None)

    return alert


def dict_to_user(user: dict):
    #из жсон юзера обратно в объект юзера
    newUser = User(user['username'], user['telegram_user_id'])
    newUser.first_joined = user['first_joined']
    newUser.alerts = [dict_to_alert(x) for x in user['alerts']]
    return newUser
    
def alert_to_dict(alert):
        #алерт в словарь жсон
        
        base = {
            'alert_id': alert.alert_id,
            'user_id': alert.user_id,
            'active': alert.active,
            'zone_percent': alert.zone_percent,
            'created_at': alert.created_at,
            'type': type(alert).__name__,  # сохраняем имя класса
            'last_triggered_price': alert.last_triggered_price,
            'last_triggered_at': alert.last_triggered_at
            }
        
        if isinstance(alert, PriceTargetAlert):
            base['price_target'] = alert.price_target
            base['place'] = alert.place
            base['direction'] = alert.direction
            

        elif isinstance(alert, PercentTargetAlert):
            base['direction'] = alert.direction
            base['percent_target'] = alert.percent_target
            base['place'] = alert.place
            base['initial_price'] = alert.initial_price
            
        
        elif isinstance(alert, P2PMerchantAlert):
            base['minimum_completed_orders'] = alert.minimum_completed_orders
            base['completion_rate'] = alert.completion_rate
            base['exchange'] = alert.exchange 
            base['required_banks'] = alert.required_banks

        elif isinstance(alert, ArbitrageAlert):
            base['goal_spread'] = alert.goal_spread
            base['arb_type'] = alert.arb_type
            base['last_triggered_spread'] = alert.last_triggered_spread
            base['last_triggered_spread_price'] = alert.last_triggered_spread_price

        elif isinstance(alert, SpreadAlert):
            base['goal_spread'] = alert.goal_spread
            base['bank'] = alert.bank
            base['exchange_place'] = alert.exchange_place
        return base



def user_to_dict(user) -> dict:
    #из юзера в словарь, алерты список словарей параметров алерта
    return {
        'username': user.username,
        'telegram_user_id': user.telegram_user_id,
        'first_joined': user.first_joined,
        'alerts': [alert_to_dict(a) for a in user.alerts]
    }
def load_users() -> dict:
    # если файл не существует — вернуть пустой словарь
    # иначе прочитать и вернуть содержимое

    if not DATA_FILE.exists():
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Ошибка чтения users.json: {e}")
        return {}
    

def save_users(users: dict) -> None:
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=4)




    
def save_user(user: User) -> None:
    users = load_users()
    users[user.telegram_user_id] = user_to_dict(user)
    save_users(users)

def get_user(telegram_user_id: str, username: str = ""):
    users = load_users()
    if telegram_user_id in users:
        newUser = dict_to_user(users[telegram_user_id])
        return newUser
    else:
        newUser = User(username, telegram_user_id)
        save_user(newUser)
        return newUser



