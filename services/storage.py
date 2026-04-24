import json
from models.user import User
from models.alert import Alert, PriceTargetAlert, PercentTargetAlert, ArbitrageAlert, SpreadAlert, P2PMerchantAlert
from pathlib import Path
from asyncpg import Connection
from services.database import get_pool
from collections import defaultdict
from datetime import datetime





    
def alert_to_row(alert: Alert):
        #алерт данные алерта для инсерта в таблицу алертов

        
        if isinstance(alert, PriceTargetAlert):
            data = {'price_target': alert.price_target, 'place': alert.place, 'direction': alert.direction}
            

        elif isinstance(alert, PercentTargetAlert):
            data = {'direction': alert.direction, 'percent_target': alert.percent_target, 'place': alert.place, 'initial_price': alert.initial_price}
            
        
        elif isinstance(alert, P2PMerchantAlert):
            data = {'minimum_completed_orders':alert.minimum_completed_orders,' completion_rate':alert.completion_rate, 'exchange':alert.exchange, 'required_banks':alert.required_banks}

        elif isinstance(alert, ArbitrageAlert):
            data = {'goal_spread': alert.goal_spread, 'arb_type': alert.arb_type, 'last_triggered_spread':alert.last_triggered_spread, 'last_triggered_spread_price': alert.last_triggered_spread_price}

        elif isinstance(alert, SpreadAlert):
            data = {'goal_spread': alert.goal_spread, 'bank': alert.bank, 'exchange_place': alert.exchange_place}
        else:
            raise ValueError(f"Неизвестный тип: {type(alert).__name__}")
        
        created_at = datetime.fromisoformat(alert.created_at)
        last_triggered_at = datetime.fromisoformat(alert.last_triggered_at) if alert.last_triggered_at else None
        

        
        
        return (alert.alert_id, alert.user_id, alert.active, alert.zone_percent, 
        created_at, type(alert).__name__, alert.last_triggered_price, 
        last_triggered_at, json.dumps(data))

async def save_alert(conn: Connection, alert: Alert):
    await conn.execute("""
                       INSERT INTO alerts (alert_id, user_id, active, zone_percent, created_at, type, last_triggered_price, last_triggered_at, data) 
                       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                       ON CONFLICT (alert_id) DO UPDATE SET
                       active = EXCLUDED.active,
                       last_triggered_price = EXCLUDED.last_triggered_price,
                       last_triggered_at = EXCLUDED.last_triggered_at,
                       data = EXCLUDED.data
                       """, *alert_to_row(alert))

async def delete_alert(conn: Connection, alert: Alert):
    await conn.execute("DELETE FROM alerts WHERE alert_id = $1", alert.alert_id)

async def clear_alerts(conn: Connection, telegram_user_id: str):
    await conn.execute("DELETE FROM alerts WHERE user_id = $1", telegram_user_id)






async def load_users(conn: Connection):
    pool = await get_pool()

    async with pool.acquire() as conn:
        users_db = await conn.fetch("SELECT * FROM users")
        alerts_db = await conn.fetch("SELECT * FROM alerts")

        users = []
        alerts = defaultdict(list)
        for row in alerts_db:
                alerts[row["user_id"]].append(row_to_alert(row))

        for us in users_db:
            user = User(us["username"], us["telegram_user_id"], str(us["first_joined"]), alerts[us["telegram_user_id"]])

            users.append(user)
        return users
    

    
    




async def save_user(conn: Connection, user: User):
    await conn.execute("""INSERT INTO users(telegram_user_id, username) 
                       VALUES ($1, $2)
                       ON CONFLICT (telegram_user_id) DO UPDATE SET
                       username = EXCLUDED.username
                       """, user.telegram_user_id, user.username)
    




def row_to_alert(row: dict):
    alert = None
    alert_type = row["type"]
    data = row["data"]
    alert_id, user_id, active, zone_percent, created_at, last_triggered_price, last_triggered_at = row["alert_id"], row["user_id"], row["active"], row["zone_percent"], row["created_at"], row["last_triggered_price"], row["last_triggered_at"]
    if alert_type == "PriceTargetAlert":
        alert = PriceTargetAlert(alert_id=alert_id, user_id=user_id, active=active, zone_percent=zone_percent, created_at=created_at, last_triggered_price=last_triggered_price, last_triggered_at=last_triggered_at, price_target=data["price_target"], place=data["place"], direction= data["direction"])
    elif alert_type == "PercentTargetAlert":
        alert = PercentTargetAlert(alert_id=alert_id, user_id=user_id, active=active, zone_percent=zone_percent, created_at=created_at, last_triggered_price=last_triggered_price, last_triggered_at=last_triggered_at, direction=data["direction"], percent_target=data["percent_target"], place=data["place"], initial_price=data["initial_price"])
    elif alert_type == "P2PMerchantAlert":
        alert = P2PMerchantAlert(alert_id=alert_id, user_id=user_id, active=active, zone_percent=zone_percent, created_at=created_at, last_triggered_price=last_triggered_price, last_triggered_at=last_triggered_at, minimum_completed_orders=data["minimum_completed_orders"], completion_rate=data["completion_rate"], exchange=data["exchange"], required_banks=data["required_banks"])
    elif alert_type == "ArbitrageAlert":
        #допишу потом когда будет окх и я сам сделаю арбитраж нормальный с добавлением новых фич
        pass 
    elif alert_type == "SpreadAlert":
        #та же логика как и сверху
        pass
    return alert




async def get_alerts(conn: Connection, telegram_user_id: str):
    
    rows = await conn.fetch("SELECT * from alerts where user_id = $1", telegram_user_id)
    alerts = []
    for row in rows:
        alert = row_to_alert(row)

        if alert is not None:
            alerts.append(alert)

    return alerts




async def get_user(telegram_user_id: str, username: str = ""):
    pool = await get_pool()
    async with pool.acquire() as conn:
        user_row = await conn.fetchrow("SELECT * from users where telegram_user_id = $1", telegram_user_id)

        if user_row:
            user = User(username=user_row["username"], telegram_user_id=user_row["telegram_user_id"], first_joined=str(user_row["first_joined"]))
            # момент с загружением алертов как я понял на будущую функцию
            user.alerts = await get_alerts(conn, telegram_user_id)
        else:
            await conn.execute("INSERT INTO users (telegram_user_id, username) VALUES ($1, $2)", telegram_user_id, username) #в таблийе дб по дефолту now уже есть для джойнед
            user = User(telegram_user_id=telegram_user_id, username=username)
        return user
        

            

