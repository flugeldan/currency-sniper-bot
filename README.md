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
- FSM — управление диалогами
- Неофициальные P2P API Binance и Bybit (reverse engineered через DevTools)

## Архитектура
currency_sniper_bot/
├── Main.py              # точка входа
├── config.py            # переменные окружения
├── texts.py             # форматирование сообщений
├── handlers/
│   ├── start.py         # основные хендлеры
│   ├── alerts.py        # создание и управление алертами
│   └── keyboards.py     # клавиатуры и инлайн кнопки
├── services/
│   ├── fetcher.py       # парсинг P2P API
│   ├── analyzer.py      # расчёт спредов и арбитража
│   ├── monitor.py       # фоновый мониторинг алертов
│   ├── cache.py         # кэш актуальных данных
│   └── storage.py       # хранение данных пользователей
└── models/
├── user.py          # модель пользователя
└── alert.py         # модели алертов

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

```bash
python Main.py
```

## Планы

- [ ] Миграция с JSON на PostgreSQL
- [ ] Redis для FSM storage и rate limiting  
- [ ] Переход на event-driven архитектуру мониторинга
- [ ] Tiered scheduling (price/percent → merchant → arbitrage)
- [ ] Добавление OKX после деплоя на европейский сервер (окх заблокирован в казахстане)
- [ ] Арбитражные алерты между биржами
- [ ] CI/CD через GitHub Actions
- [ ] Деплой на VPS с Nginx

## Автор

telegram: reidalreadytaken
made 