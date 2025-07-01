# Farming Simulator Discord Bot

Discord-бот, который отображает информацию о состоянии сервера Farming Simulator.

## Запуск локально

1. Скопируйте `.env.example` в `.env` и заполните значения.
2. Установите зависимости `pip install -r requirements.txt`.
3. Запустите `python main.py`.

## Переменные окружения

- `DISCORD_TOKEN` — токен Discord-бота
- `DISCORD_CHANNEL_ID` — ID канала для обновления сообщения
- `FTP_POLL_INTERVAL` — интервал опроса API (сек)
- `API_BASE_URL` — базовый URL API
- `API_SECRET_CODE` — секретный код API

## Railway

Приложение готово для размещения на Railway. Используется `Procfile` с командой `worker: python main.py`.
