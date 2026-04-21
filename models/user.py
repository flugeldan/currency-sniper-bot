from datetime import datetime
class User():
    def __init__(self, username: str, telegram_user_id: str):
        self.username = username
        self.telegram_user_id = telegram_user_id
        self.first_joined = datetime.now().isoformat()
        self.alerts = []
    
    def add_alert(self, alert):
        self.alerts.append(alert)
    
    def toggle_alert(self, alert_id: str):
        for cur_alert in self.alerts:
            if cur_alert.alert_id == alert_id:
                cur_alert.active = not cur_alert.active
        

    
    def remove_alert(self, alert):
        self.alerts.remove(alert)
        
    def clear_alerts(self):
        self.alerts = []
    
    def get_active_alerts(self):
        active_alerts = [alert for alert in self.alerts if alert.active]
        return active_alerts
