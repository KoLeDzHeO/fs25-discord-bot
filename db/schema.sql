-- Таблица сырой истории онлайна
CREATE TABLE IF NOT EXISTS player_online_history (
    player_name TEXT NOT NULL,
    check_time TIMESTAMP NOT NULL
);

-- Гарантируем уникальность записи игрока в конкретный момент времени
CREATE UNIQUE INDEX IF NOT EXISTS idx_player_online_history_unique
    ON player_online_history (player_name, check_time);

-- Таблица недельного топа
CREATE TABLE IF NOT EXISTS player_top_week (
    player_name TEXT UNIQUE NOT NULL,
    activity_hours INTEGER NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- Таблица общего времени игры
CREATE TABLE IF NOT EXISTS player_total_time (
    id SERIAL PRIMARY KEY,
    player_name TEXT UNIQUE NOT NULL,
    total_hours INTEGER NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
