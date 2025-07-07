-- Таблица сырой истории онлайна
CREATE TABLE IF NOT EXISTS player_online_history (
    player_name TEXT NOT NULL,
    check_time TIMESTAMP NOT NULL
);

-- Таблица недельного топа
CREATE TABLE IF NOT EXISTS player_top_week (
    player_name TEXT NOT NULL,
    activity_hours INTEGER NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
