from os import getenv
from dotenv import load_dotenv
load_dotenv()
TOKEN = getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env файле")

CHECK_INTERVAL = 60 # раз в минуту он будет проверять курсы

