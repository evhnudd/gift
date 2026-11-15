-- ==========================================
-- Система учета подарков: структура базы данных
-- ==========================================
-- Сущности предметной области:
--   users  - пользователи (они же получатели подарков);
--   gifts  - подарки, каждый относится к одному получателю;
--   events - события календаря (день рождения, праздник),
--            связанные с пользователем и, при наличии, с подарком.
--
-- Связи:
--   gifts.recipient_id -> users.id  (один пользователь - много подарков)
--   events.user_id     -> users.id  (один пользователь - много событий)
--   events.gift_id     -> gifts.id  (подарок может быть привязан к событию)

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS gifts (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    recipient_id INTEGER NOT NULL,
    price REAL NOT NULL CHECK (price >= 0),
    delivery_cost REAL NOT NULL DEFAULT 0 CHECK (delivery_cost >= 0),
    delivery_date TEXT NOT NULL,
    is_purchased INTEGER NOT NULL DEFAULT 0 CHECK (is_purchased IN (0, 1)),
    FOREIGN KEY (recipient_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    event_date TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    gift_id INTEGER,
    description TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (gift_id) REFERENCES gifts(id)
);
