# 💱 Currency Sniper Bot
Telegram-бот для мониторинга P2P курсов USDT/KZT на Binance и Bybit с системой алертов и аналитикой спредов.

## Что умеет
- 📊 Актуальные P2P курсы Binance и Bybit в реальном времени
- 🏦 Сравнение с официальным курсом НБК
- 💱 Арбитражные спреды между биржами и относительно НБК
- 🥇 Топ-10 мерчантов с фильтрацией и переключением buy/sell
- 🎯 Система алертов: целевая цена, изменение в %, поиск мерчанта
- 🔔 Управление алертами: пауза, удаление, пагинация
- 🔄 Данные обновляются каждую минуту в фоне

## Стек
- Python 3.9
- aiogram 3.x — Telegram Bot framework
- aiohttp — асинхронные HTTP запросы
- asyncpg — асинхронный драйвер PostgreSQL
- PostgreSQL — основная БД
- FSM — управление диалогами
- Неофициальные P2P API Binance и Bybit (reverse engineered через DevTools)

## Архитектура
currency_sniper_bot/
├── Main.py                     # точка входа
├── config.py                   # переменные окружения
├── texts.py                    # форматирование сообщений
├── schema.sql                  # схема БД
├── .env.example                # шаблон переменных окружения
├── handlers/
│   ├── start.py                # основные хендлеры
│   ├── alerts.py               # создание и управление алертами
│   └── keyboards.py            # клавиатуры и инлайн кнопки
├── middlewares/
│   └── repo_middleware.py      # dependency injection через aiogram middleware
├── repository/
│   └── user_repository.py      # Repository pattern с in-memory кэшем
├── services/
│   ├── fetcher.py              # парсинг P2P API
│   ├── analyzer.py             # расчёт спредов и арбитража
│   ├── monitor.py              # фоновый мониторинг алертов
│   ├── cache.py                # кэш актуальных курсов
│   ├── database.py             # asyncpg connection pool
│   └── storage.py              # низкоуровневые SQL операции
└── models/
├── user.py                 # модель пользователя
└── alert.py                # модели алертов

## Архитектурные решения
- **Repository pattern** — единая точка доступа к данным, скрывает детали БД от хендлеров
- **In-memory кэш** — юзеры и алерты хранятся в памяти, БД как персистентность при перезапуске
- **Гранулярные операции** — `save_alert` / `delete_alert` вместо полной перезаписи юзера
- **Dependency injection** — `repo` передаётся в хендлеры через aiogram middleware
- **Upsert** — `INSERT ... ON CONFLICT DO UPDATE` для идемпотентного сохранения

## Запуск

```bash
git clone https://github.com/flugeldan/currency-sniper-bot
cd currency-sniper-bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Создай `.env`:
BOT_TOKEN=your_token_here
DATABASE_URL=postgresql://user:password@localhost:5432/currency_sniper

Создай БД и таблицы:
```bash
psql -U postgres -c "CREATE DATABASE currency_sniper;"
psql -U postgres -d currency_sniper -f schema.sql
```

Запусти:
```bash
python Main.py
```

## Планы
- [ ] Redis для FSM storage и rate limiting
- [ ] Переход на event-driven архитектуру мониторинга
- [ ] Tiered scheduling (price/percent → merchant → arbitrage)
- [ ] Добавление OKX после деплоя на европейский сервер
- [ ] Арбитражные алерты между биржами
- [ ] CI/CD через GitHub Actions
- [ ] Деплой на VPS

## Автор
telegram: reidalreadytaken