
from datetime import datetime
import uuid
class Alert():
    

    def __init__(self, user_id: int, active: bool, zone_percent: int):
        self.alert_id = str(uuid.uuid4())
        self.user_id = user_id
        self.active = active
        self.zone_percent = zone_percent
        self.created_at = datetime.now().isoformat()
        self.last_triggered_price = None
        self.last_triggered_at = None


class PriceTargetAlert(Alert):
    def __init__(self, user_id: int, active: bool, zone_percent: int, price_target: float, place: str, initial_price: float):
        super().__init__(user_id, active, zone_percent)
        self.price_target = price_target
        self.place = place
        self.direction = 'up' if price_target > initial_price else 'down'

class PercentTargetAlert(Alert):
    def __init__(self, user_id: int, active: bool, zone_percent: int, percent_target: float, direction: str, place: str, initial_price: float):
        super().__init__(user_id, active, zone_percent)
        self.direction = direction
        self.percent_target = percent_target 
        self.place = place 
        self.initial_price = initial_price
        
class P2PMerchantAlert(Alert):
    def __init__(self, user_id: int, active: bool, zone_percent: int, minimum_completed_orders: int, completion_rate: float, exchange: str, required_banks: list):
        super().__init__(user_id, active, zone_percent)
        self.minimum_completed_orders = minimum_completed_orders
        self.completion_rate = completion_rate
        self.exchange = exchange 
        self.required_banks = required_banks


class ArbitrageAlert(Alert):
    def __init__(self, user_id: int, active: bool, zone_percent: int, goal_spread: float, arb_type: str):
        super().__init__(user_id, active, zone_percent)
        self.goal_spread = goal_spread
        self.arb_type = arb_type
        self.last_triggered_spread = None
        self.last_triggered_spread_price = None

class SpreadAlert(Alert):
    def __init__(self, user_id: int, active: bool, zone_percent: int, goal_spread: float, bank: str, exchange_place: str):
        super().__init__(user_id, active, zone_percent)
        self.goal_spread = goal_spread
        self.bank = bank
        self.exchange_place = exchange_place



        

