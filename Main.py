import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import TOKEN
from handlers.start import router as start_router
from services.monitor import monitor_loop
from handlers.alerts import router as alerts_router
from services.database import get_pool
from repository.user_repository import UserRepository
from middlewares.repo_middleware import RepoMiddleware
from services.logger import setup_logger
setup_logger()

async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    pool = await get_pool()
    repo = UserRepository(pool)
    dp.message.middleware(RepoMiddleware(repo))
    dp.callback_query.middleware(RepoMiddleware(repo))
    
    dp.include_router(alerts_router)
    dp.include_router(start_router)
    
    asyncio.create_task(monitor_loop(bot, repo))
    await dp.start_polling(bot)  # передаём repo в хендлеры

asyncio.run(main())