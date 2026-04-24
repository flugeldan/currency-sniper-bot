from services.storage import (
    get_user as db_get_user,
    load_users as db_load_users,
    save_user as db_save_user,
    save_alert as db_save_alert,
    delete_alert as db_delete_alert,
    clear_alerts as db_clear_alerts
    
)
from models.alert import Alert
class UserRepository:
    def __init__(self, pool):
        self.pool = pool
        self._cache = {}          

    async def get_user(self, telegram_user_id: str, username: str = ""):
        if telegram_user_id in self._cache:
            if username and self._cache[telegram_user_id].username != username:
                
                self._cache[telegram_user_id].username = username
                async with self.pool.acquire() as conn:
                    await db_save_user(conn, self._cache[telegram_user_id])
            
            return self._cache[telegram_user_id]
        
        user = await db_get_user(telegram_user_id, username)
        
        self._cache[telegram_user_id] = user

        return user
    
    async def get_all_users(self):
        if self._cache:
            return list(self._cache.values())
        
        users = await db_load_users()

        for user in users:
            self._cache[user.telegram_user_id] = user
    
        return list(self._cache.values())
    
    async def clear_alerts(self, telegram_user_id: str):
        async with self.pool.acquire() as conn:
            await db_clear_alerts(conn, telegram_user_id)

        if self._cache[telegram_user_id]:
            self._cache[telegram_user_id].clear_alerts()
        


        

        

    
    async def save_alert(self, alert: Alert):

        async with self.pool.acquire() as conn:
            await db_save_alert(conn, alert)
            
        
    async def delete_alert(self,alert: Alert):

        async with self.pool.acquire() as conn:
            await db_delete_alert(conn, alert)
            
    

        

        
