CREATE TABLE users (
    telegram_user_id TEXT PRIMARY KEY,
    username TEXT,
    first_joined TIMESTAMP DEFAULT NOW()
);

CREATE TABLE alerts (
    alert_id UUID PRIMARY KEY,
    user_id TEXT REFERENCES users(telegram_user_id) ON DELETE CASCADE,
    type TEXT NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    zone_percent FLOAT,
    created_at TIMESTAMP DEFAULT NOW(),
    last_triggered_price FLOAT,
    last_triggered_at TIMESTAMP,
    data JSONB
);