import asyncio
from aiogram import Bot, Dispatcher
from config import TOKEN
from handlers.start import router as start_router
from services.monitor import monitor_loop
from handlers.alerts import router as alerts_router


async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(alerts_router)
    dp.include_router(start_router)
    asyncio.create_task(monitor_loop(bot))
    await dp.start_polling(bot)

asyncio.run(main())