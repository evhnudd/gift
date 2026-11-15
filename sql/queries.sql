-- ==========================================
-- Система учета подарков: SQL-запросы проекта (ПР7)
-- ==========================================
-- Проверка в SQLite CLI из корня проекта:
--     sqlite3 data/gifts.sqlite
--     .headers on
--     .mode column
--
-- Значения 5000, 2026-12-01, 2 и т. п. указаны для проверки в CLI.
-- В Django-представлениях они передаются параметрами ? (gift_web/views.py).


-- ------------------------------------------
-- 1. ВЫБОРКА СПИСКОВ
-- ------------------------------------------

-- Запрос 1. Список пользователей (страница «Пользователи»)
SELECT
    id,
    name,
    email
FROM users
ORDER BY name;

-- Запрос 2. Список подарков с полной стоимостью (страница «Подарки»)
SELECT
    id,
    name,
    price,
    delivery_cost,
    price + delivery_cost AS total_cost,
    delivery_date,
    is_purchased
FROM gifts
ORDER BY name;

-- Запрос 3. Три самых дорогих подарка (блок на странице «Статистика»)
SELECT
    name,
    price + delivery_cost AS total_cost
FROM gifts
ORDER BY total_cost DESC
LIMIT 3;


-- ------------------------------------------
-- 2. ФИЛЬТРАЦИЯ (WHERE)
-- ------------------------------------------

-- Запрос 4. Подарки, укладывающиеся в бюджет (страница «Поиск по бюджету»)
-- В приложении: WHERE price + delivery_cost <= ?
SELECT
    id,
    name,
    price + delivery_cost AS total_cost
FROM gifts
WHERE price + delivery_cost <= 5000
ORDER BY total_cost;

-- Запрос 5. Еще не заказанные подарки (фильтр «Не заказаны» на странице «Подарки»)
-- В приложении: WHERE gifts.is_purchased = ?
SELECT
    id,
    name,
    delivery_date
FROM gifts
WHERE is_purchased = 0
ORDER BY delivery_date;

-- Запрос 6. События в заданном периоде (фильтр по датам на странице «События»)
-- В приложении: WHERE events.event_date BETWEEN ? AND ?
SELECT
    id,
    title,
    event_date
FROM events
WHERE event_date BETWEEN '2026-12-01' AND '2026-12-31'
ORDER BY event_date;

-- Запрос 7. События без описания (проверка NULL)
SELECT
    id,
    title
FROM events
WHERE description IS NULL;


-- ------------------------------------------
-- 3. СОЕДИНЕНИЕ ТАБЛИЦ (JOIN)
-- ------------------------------------------

-- Запрос 8. Подарки вместе с получателем и статусом (страницы «Подарки»,
-- карточка подарка, подарки получателя)
SELECT
    gifts.id,
    gifts.name,
    users.id AS recipient_id,
    users.name AS recipient_name,
    gifts.price,
    gifts.delivery_cost,
    gifts.price + gifts.delivery_cost AS total_cost,
    gifts.delivery_date,
    CASE
        WHEN gifts.is_purchased = 1 AND gifts.delivery_date >= date('now')
            THEN 'Подарок заказан и ожидается'
        WHEN gifts.is_purchased = 1
            THEN 'Подарок заказан, но дата доставки прошла'
        ELSE 'Подарок еще не заказан'
    END AS status
FROM gifts
JOIN users
    ON gifts.recipient_id = users.id
ORDER BY gifts.name;

-- Запрос 9. События с именем пользователя и названием подарка
-- (страница «События», соединение трех таблиц)
SELECT
    events.id,
    events.title,
    events.event_date,
    users.name AS user_name,
    gifts.name AS gift_name
FROM events
JOIN users
    ON events.user_id = users.id
LEFT JOIN gifts
    ON events.gift_id = gifts.id
ORDER BY events.event_date;

-- Запрос 10. Подарки конкретного получателя (страница получателя)
-- В приложении: WHERE users.id = ?
SELECT
    users.name AS recipient_name,
    gifts.name AS gift_name,
    gifts.price + gifts.delivery_cost AS total_cost
FROM gifts
JOIN users
    ON gifts.recipient_id = users.id
WHERE users.id = 1
ORDER BY gifts.name;


-- ------------------------------------------
-- 4. АГРЕГАТНЫЕ ФУНКЦИИ
-- ------------------------------------------

-- Запрос 11. Количество записей в таблицах (главная страница)
SELECT
    (SELECT COUNT(*) FROM users) AS users_count,
    (SELECT COUNT(*) FROM gifts) AS gifts_count,
    (SELECT COUNT(*) FROM events) AS events_count;

-- Запрос 12. Сводка по подаркам (страница «Статистика»)
SELECT
    COUNT(*) AS gifts_count,
    SUM(price + delivery_cost) AS total_sum,
    ROUND(AVG(price + delivery_cost), 2) AS average_cost,
    MIN(price + delivery_cost) AS min_cost,
    MAX(price + delivery_cost) AS max_cost
FROM gifts;

-- Запрос 13. Сумма уже заказанных подарков
SELECT
    COUNT(*) AS purchased_count,
    SUM(price + delivery_cost) AS purchased_sum
FROM gifts
WHERE is_purchased = 1;


-- ------------------------------------------
-- 5. ГРУППИРОВКА (GROUP BY) И ФИЛЬТРАЦИЯ ГРУПП (HAVING)
-- ------------------------------------------

-- Запрос 14. Количество и сумма подарков по каждому получателю
-- (страницы «Получатели» и «Статистика»). LEFT JOIN сохраняет
-- получателей без подарков с количеством 0.
SELECT
    users.id,
    users.name AS recipient_name,
    COUNT(gifts.id) AS gifts_count,
    COALESCE(SUM(gifts.price + gifts.delivery_cost), 0) AS total_sum
FROM users
LEFT JOIN gifts
    ON gifts.recipient_id = users.id
GROUP BY users.id, users.name
ORDER BY gifts_count DESC, users.name;

-- Запрос 15. Подарки по статусу заказа (страница «Статистика»)
SELECT
    is_purchased,
    COUNT(*) AS gifts_count,
    SUM(price + delivery_cost) AS total_sum
FROM gifts
GROUP BY is_purchased
ORDER BY is_purchased;

-- Запрос 16. Получатели, которым запланировано не меньше N подарков (HAVING)
-- В приложении: HAVING COUNT(gifts.id) >= ?
SELECT
    users.name AS recipient_name,
    COUNT(gifts.id) AS gifts_count
FROM users
JOIN gifts
    ON gifts.recipient_id = users.id
GROUP BY users.id, users.name
HAVING COUNT(gifts.id) >= 2
ORDER BY gifts_count DESC;
