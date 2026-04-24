from datetime import datetime
import uuid

class Alert():
    def __init__(self, user_id: int, active: bool, zone_percent: int,
                 alert_id: str = None, created_at: str = None,
                 last_triggered_price: float = None, last_triggered_at: str = None):
        self.alert_id = alert_id or str(uuid.uuid4())
        self.user_id = user_id
        self.active = active
        self.zone_percent = zone_percent
        self.created_at = created_at or datetime.now().isoformat()
        self.last_triggered_price = last_triggered_price
        self.last_triggered_at = last_triggered_at


class PriceTargetAlert(Alert):
    def __init__(self, user_id: int, active: bool, zone_percent: int,
                 price_target: float, place: str,
                 initial_price: float = None, direction: str = None,
                 **kwargs):
        super().__init__(user_id, active, zone_percent, **kwargs)
        self.price_target = price_target
        self.place = place
        if direction is not None:
            self.direction = direction
        elif initial_price is not None:
            self.direction = 'up' if price_target > initial_price else 'down'
        else:
            raise ValueError("PriceTargetAlert требует либо direction, либо initial_price")


class PercentTargetAlert(Alert):
    def __init__(self, user_id: int, active: bool, zone_percent: int,
                 percent_target: float, direction: str, place: str, initial_price: float,
                 **kwargs):
        super().__init__(user_id, active, zone_percent, **kwargs)
        self.direction = direction
        self.percent_target = percent_target
        self.place = place
        self.initial_price = initial_price


class P2PMerchantAlert(Alert):
    def __init__(self, user_id: int, active: bool, zone_percent: int,
                 minimum_completed_orders: int, completion_rate: float,
                 exchange: str, required_banks: list,
                 **kwargs):
        super().__init__(user_id, active, zone_percent, **kwargs)
        self.minimum_completed_orders = minimum_completed_orders
        self.completion_rate = completion_rate
        self.exchange = exchange
        self.required_banks = required_banks


class ArbitrageAlert(Alert):
    def __init__(self, user_id: int, active: bool, zone_percent: int,
                 goal_spread: float, arb_type: str,
                 last_triggered_spread=None, last_triggered_spread_price=None,
                 **kwargs):
        super().__init__(user_id, active, zone_percent, **kwargs)
        self.goal_spread = goal_spread
        self.arb_type = arb_type
        self.last_triggered_spread = last_triggered_spread
        self.last_triggered_spread_price = last_triggered_spread_price


class SpreadAlert(Alert):
    def __init__(self, user_id: int, active: bool, zone_percent: int,
                 goal_spread: float, bank: str, exchange_place: str,
                 **kwargs):
        super().__init__(user_id, active, zone_percent, **kwargs)
        self.goal_spread = goal_spread
        self.bank = bank
        self.exchange_place = exchange_place