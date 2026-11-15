# Система учета подарков

## Назначение

Консольное приложение помогает планировать подарки, учитывать их стоимость и проверять статус заказа. На следующих практических работах проект может быть расширен до веб-приложения на Django.

## Целевая аудитория

Пользователи, которые планируют подарки для семьи, друзей и коллег и хотят контролировать бюджет и доставку.

## Предметная область

Приложение работает с подарками, их получателями, стоимостью, доставкой, датой доставки и состоянием заказа.

## Основные сущности

- Подарок: название, стоимость и статус заказа.
- Получатель: человек, которому предназначен подарок.
- Доставка: стоимость и планируемая дата доставки.
- Бюджет: допустимая сумма покупки.

## Основные функции

- Расчет общей стоимости подарка с учетом доставки.
- Проверка, укладывается ли подарок в заданный бюджет.
- Определение статуса заказа и доставки подарка.

## План развития

- Добавить коллекции подарков и несколько сценариев работы.
- Разнести код по модулям и добавить обработку ошибок.
- Реализовать сущности проекта в виде классов.
- Создать веб-приложение на Django.
- Подключить базу данных и реализовать CRUD-операции.
- Добавить регистрацию пользователей и разграничение доступа.
- Разработать REST API.
- Контейнеризировать приложение в Docker и настроить CI/CD.

## Запуск

```text
python main.py
```

Для запуска тестов:

```text
pytest -q
```

## Содержание ПР1

В проекте использованы простые типы данных, арифметические операции, преобразование и сравнение значений, условные конструкции, функции и импорт стандартного модуля `datetime`.

Доступа к Яндекс Практикуму нет, поэтому выполнение внешних учебных заданий курса не может быть подтверждено этим репозиторием. Практическая часть проекта, тесты и документация подготовлены локально.

## Содержание ПР2

Во второй практической работе консольный сценарий ПР1 расширен до программы,
работающей с коллекцией подарков. Логика разделена на модули, данные хранятся
в JSON-файле, добавлены обработка ошибок ввода, меню и автоматические тесты.

## Возможности ПР2

- просмотр списка подарков и заказанных подарков;
- добавление и поиск подарков по названию или получателю;
- расчет общей стоимости с доставкой и проверка бюджета;
- оформление и отмена заказа;
- сохранение данных между запусками приложения.

## Структура проекта

- `main.py` — меню и вывод данных;
- `gifts.py` — класс `Gift` и функции обработки коллекции подарков;
- `users.py` — класс `User` и функции обработки пользователей;
- `storage.py` — загрузка и сохранение JSON;
- `utils.py` — безопасный ввод чисел и дат;
- `data/gifts.json` — данные приложения;
- `data/users.json` — пользователи приложения;
- `data/settings.json` — настройки и бюджет приложения;
- `tests/` — дополнительные тесты ПР2;
- `test_main.py` — тесты функций, сохраненных из ПР1.

## Требования

- Python 3.12 или новее;
- pytest;
- flake8.

Подготовка окружения в PowerShell Windows:

```powershell
python -m venv .venv
& .\.venv\bin\Activate.ps1
python -m pip install -r requirements.txt
```

Если окружение уже создано, команды проекта можно выполнять без активации:

```powershell
.\.venv\bin\python.exe -m pytest -q
.\.venv\bin\flake8.exe main.py gifts.py storage.py utils.py test_main.py tests
```

Установка зависимостей:

```text
python -m pip install -r requirements.txt
```

Запуск программы:

```text
python main.py
```

Запуск тестов:

```text
pytest -q
```

Проверка качества кода:

```text
flake8 main.py gifts.py storage.py utils.py test_main.py tests
```

Для отладки в VS Code выберите конфигурацию «Запуск системы учета подарков»
из `.vscode/launch.json`, установите breakpoint в `main.py` и запустите F5.

Подробный отчет по практической работе находится в разделе «Отчет по
практической работе № 2» файла `REPORT.md`.

## Содержание ПР3

В третьей практической работе функциональная модель проекта переработана в
объектно-ориентированную. Основные сущности предметной области представлены
классами `Gift` и `User`, а коллекции хранятся как `list[Gift]` и `list[User]`.

### Класс Gift

Класс `Gift` хранит:

- `id` — идентификатор подарка;
- `name` — название;
- `recipient` — получатель;
- `price` — стоимость подарка;
- `delivery_cost` — стоимость доставки;
- `delivery_date` — дата доставки типа `date`;
- `is_purchased` — состояние заказа.

Основные методы класса:

- `total_cost()` — считает полную стоимость;
- `is_within_budget()` — проверяет бюджет;
- `order()` и `cancel_order()` — изменяют состояние заказа;
- `status()` — возвращает статус подарка;
- `__str__()` — формирует строковое представление;
- `from_data()` — создает объект из записи JSON;
- `to_data()` — преобразует объект в структуру для JSON.

Функции `find_gifts()`, `filter_gifts_by_budget()` и `sort_gifts()` работают
с коллекцией объектов `Gift`. Функции `add_gift()`, `order_gift()` и
`cancel_order()` организуют операции над коллекцией, а состояние конкретного
подарка изменяется его методами.

### Класс User

Класс `User` хранит идентификатор, имя и электронную почту получателя. Он
реализует `__init__`, `__str__`, `from_data()` и `to_data()`. Объект `Gift`
содержит ссылку на объект `User` в атрибуте `recipient`.

### Хранение данных

`storage.py` преобразует записи JSON в объекты `Gift` и `User` при загрузке и
объекты обратно в JSON при сохранении. В проекте используются три файла данных:

- `data/gifts.json` — подарки и `recipient_id`;
- `data/users.json` — пользователи-получатели;
- `data/settings.json` — настройки и бюджет по умолчанию.

При загрузке подарков `recipient_id` связывается с объектом `User`. Старый формат
с текстовым полем `recipient` поддерживается для совместимости с ПР2.

### Актуальная структура

- `gifts.py` — класс `Gift` и функции обработки коллекции;
- `storage.py` — загрузка и сохранение объектов в JSON;
- `main.py` — консольное меню и пользовательские сценарии;
- `utils.py` — безопасный ввод чисел и дат;
- `tests/` — тесты объектной модели и хранения;
- `test_main.py` — тесты функций, сохраненных из ПР1.

В ПР3 добавлены тесты создания объекта, его методов, строкового представления,
восстановления из JSON, связи с `User` и сохранения состояния заказа. Полная проверка выполняется
командами:

```text
pytest -q
flake8 main.py gifts.py storage.py utils.py test_main.py tests
```
# Веб-часть Django (ПР5–ПР6)

Проект сохраняет консольное приложение и JSON-хранилище из ПР3. Для веб-интерфейса
добавлены Django-проект `gift_project` и приложение `gift_web`.

## Запуск

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

Основные страницы:

- `/` — главная страница и навигация;
- `/users/` — пользователи;
- `/recipients/` — получатели и назначенные подарки;
- `/gifts/` — подарки;
- `/events/` — события.

Веб-часть загружает объекты `User`, `Gift` и `Event` из JSON-файлов,
использует именованные маршруты и Django Templates. ORM на этом этапе не
используется согласно заданию. Общая разметка находится в `base.html`,
навигация и карточка подарка подключаются через `{% include %}`, а CSS,
изображение и JavaScript подключаются через `{% load static %}`. В шаблонах
используются наследование, блоки, циклы, условия, `{% empty %}` и фильтры.

Проверка Django-части:

```powershell
.\.venv\bin\python.exe manage.py check
.\.venv\bin\python.exe manage.py test
.\.venv\bin\pytest.exe -q
.\.venv\bin\flake8.exe gift_project gift_web
```

Результат проверки: `manage.py check` без ошибок, Django-тесты `3 passed`,
общий набор pytest `12 passed`, замечаний flake8 нет.

# Слой базы данных SQLite (ПР7)

> С ПР9 веб-часть работает через Django ORM (см. раздел «Django ORM» ниже).
> Файлы ПР7 (`sql/`, `db/database.py`, `db/import_json.py`,
> `data/gifts.sqlite`) сохранены как предыдущая реализация и как
> **исходная база** для переноса данных в модели Django.

## Текущий этап разработки

На ПР7 данные системы учета подарков перенесены из JSON в базу данных SQLite:

- создана база данных `data/gifts.sqlite`;
- таблицы созданы с помощью `sql/schema.sql`;
- данные перенесены из JSON скриптом `db/import_json.py`;
- SQL-запросы сохранены в `sql/queries.sql` (16 запросов);
- Django-представления получают данные из SQLite через `sqlite3`
  и `sqlite3.Row`;
- страницы пользователей, получателей, подарков, событий, поиска подарков
  по бюджету и статистики работают с базой данных.

JSON-файлы и модули ПР1–ПР3 (`storage.py`, `gifts.py`, `users.py`) сохранены:
консольное приложение по-прежнему работает с JSON, а JSON-файлы служат
исходными данными для импорта. Django ORM на этом этапе не используется.

## Структура базы данных

Таблица `users` — пользователи (они же получатели подарков):

| Поле  | Тип     | Назначение                          |
|-------|---------|-------------------------------------|
| id    | INTEGER | идентификатор, первичный ключ       |
| name  | TEXT    | имя, NOT NULL                       |
| email | TEXT    | электронная почта, NOT NULL, UNIQUE |

Таблица `gifts` — подарки:

| Поле          | Тип     | Назначение                                  |
|---------------|---------|---------------------------------------------|
| id            | INTEGER | идентификатор, первичный ключ               |
| name          | TEXT    | название, NOT NULL                          |
| recipient_id  | INTEGER | внешний ключ на `users.id`, NOT NULL        |
| price         | REAL    | стоимость подарка, `CHECK (price >= 0)`     |
| delivery_cost | REAL    | стоимость доставки, DEFAULT 0               |
| delivery_date | TEXT    | дата доставки в формате `YYYY-MM-DD`        |
| is_purchased  | INTEGER | признак заказа: 0 — не заказан, 1 — заказан |

Таблица `events` — события календаря:

| Поле        | Тип     | Назначение                                     |
|-------------|---------|------------------------------------------------|
| id          | INTEGER | идентификатор, первичный ключ                  |
| title       | TEXT    | название события, NOT NULL                     |
| event_date  | TEXT    | дата события в формате `YYYY-MM-DD`            |
| user_id     | INTEGER | внешний ключ на `users.id`, NOT NULL           |
| gift_id     | INTEGER | внешний ключ на `gifts.id`, допускает NULL     |
| description | TEXT    | описание, допускает NULL                       |

Связи: `gifts.recipient_id → users.id`, `events.user_id → users.id`,
`events.gift_id → gifts.id`. Проверка внешних ключей включается в
`db/database.py` командой `PRAGMA foreign_keys = ON` при каждом подключении.

## Файлы слоя базы данных

- `sql/schema.sql` — команды `CREATE TABLE IF NOT EXISTS`;
- `sql/queries.sql` — проверенные SQL-запросы с комментариями;
- `db/database.py` — `get_connection()`, `create_schema()`, `fetch_all()`,
  `fetch_one()`;
- `db/import_json.py` — перенос данных из `data/users.json`,
  `data/gifts.json`, `data/events.json` с помощью `executemany()`;
- `data/gifts.sqlite` — файл базы данных;
- `tests/test_database.py` — тесты схемы, ключей и импорта.

## Создание базы и импорт данных

```powershell
python -m db.import_json
```

Скрипт создает таблицы (если их нет), очищает их и загружает данные заново в
одной транзакции, поэтому его можно запускать повторно. Порядок импорта:
`users` → `gifts` → `events`, так как подарки и события ссылаются на
пользователей и подарки.

Проверка в интерактивном Python:

```python
import sqlite3
conn = sqlite3.connect("data/gifts.sqlite")
conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
conn.execute("PRAGMA foreign_key_list(gifts)").fetchall()
conn.execute("SELECT COUNT(*) FROM gifts").fetchone()
```

## SQL-запросы (`sql/queries.sql`)

| Вид                 | Запросы                                                        |
|---------------------|----------------------------------------------------------------|
| Выборка списков     | 1 — пользователи; 2 — подарки с полной стоимостью; 3 — топ-3 (LIMIT) |
| Фильтрация WHERE    | 4 — подарки в пределах бюджета; 5 — не заказанные; 6 — события за период (BETWEEN); 7 — события без описания (IS NULL) |
| Соединение JOIN     | 8 — подарки с получателем и статусом; 9 — события с пользователем и подарком (3 таблицы); 10 — подарки получателя |
| Агрегатные функции  | 11 — количество записей; 12 — COUNT/SUM/AVG/MIN/MAX; 13 — сумма заказанных |
| GROUP BY / HAVING   | 14 — подарки по получателям; 15 — по статусу заказа; 16 — получатели с N и более подарками (HAVING) |

Проверка в SQLite CLI:

```powershell
sqlite3 data/gifts.sqlite
.headers on
.mode column
.read sql/queries.sql
```

## Страницы, использующие SQLite

- `/` — количество пользователей, подарков и событий (запрос 11);
- `/users/`, `/users/<id>/` — пользователи (запрос 1, `WHERE id = ?`);
- `/recipients/` — получатели с количеством и суммой подарков (запрос 14);
- `/recipients/<id>/` — подарки получателя (запрос 10, JOIN);
- `/gifts/` — подарки с получателем и статусом (запрос 8), фильтр
  `?status=not_purchased|purchased` (запрос 5);
- `/gifts/search/?budget=...` — подбор подарков по бюджету (запрос 4,
  параметр `?`);
- `/events/?date_from=...&date_to=...` — события за период (запросы 6 и 9);
- `/statistics/?min_gifts=...` — статистика (запросы 3, 12, 14, 15, 16).

Значения, введенные пользователем, передаются в SQL только параметрами `?`,
например `fetch_all(GIFTS_WITHIN_BUDGET_SQL, [_today(), budget])`.
Конкатенация и f-строки для подстановки значений не используются.

## Проверка ПР7

```powershell
python manage.py check
python manage.py test
pytest -v
flake8 . --extend-exclude=venv
```

Результат: `manage.py check` — без ошибок; Django-тесты — 12 passed;
`pytest -v` — 18 passed; замечаний flake8 нет.


# Django ORM, админ-панель и формы (ПР9–ПР11)

## Быстрый запуск

```powershell
venv\Scripts\Activate.ps1          # окружение на Python 3.11 (с ПР9)
pip install -r requirements.txt
python manage.py migrate                 # таблицы Django по миграциям
python db/import_sqlite_to_orm.py        # перенос данных из data/gifts.sqlite
python manage.py createsuperuser         # доступ к /admin/
python manage.py runserver
```

Проверки:

```powershell
python manage.py check
python manage.py makemigrations --check
python manage.py showmigrations gift_web
pytest -v
flake8 . --extend-exclude=venv
```

`pytest` настроен через `pytest.ini` (pytest-django) и запускает и старые
тесты ПР1–ПР7, и тесты Django (`gift_web/tests.py`).
`python manage.py test` также работает.

## Две базы данных

| Файл | Назначение |
|------|------------|
| `data/gifts.sqlite` | исходная база ПР7, только читается при переносе |
| `db.sqlite3` | база Django (`DATABASES` в `settings.py`), с ней работает ORM |

`db.sqlite3` и каталог `media/` — локальные данные, они исключены из Git
(`.gitignore`). На новом компьютере база воссоздаётся командами `migrate` и
`python db/import_sqlite_to_orm.py`.

Выбрана стратегия «таблицы, управляемые Django, + перенос данных»: исходная
база ПР7 не изменяется, Django создаёт свои таблицы миграциями, а скрипт
переносит записи с сохранением идентификаторов и связей в порядке
`users → gifts → events`. Повторный запуск скрипта безопасен
(`update_or_create`). Структуру исходной базы показывает
`python db/inspect_source_db.py`.

## Модели (`gift_web/models.py`)

| Модель | Поля | Связи |
|--------|------|-------|
| `User` — пользователь/получатель | `name` CharField, `email` EmailField (unique), `slug` SlugField (unique) | — |
| `Gift` — подарок | `name`, `price` и `delivery_cost` DecimalField, `delivery_date` DateField, `status` (TextChoices), `total_cost` GeneratedField, `image` ImageField | `recipient` → `User` (`on_delete=PROTECT`, `related_name="gifts"`) |
| `Event` — событие | `title`, `event_date`, `description` (blank) | `user` → `User` (`CASCADE`, `related_name="events"`), `gift` → `Gift` (`SET_NULL`, `null=True`, `related_name="events"`) |

Почему так настроены связи:

* получателя с подарками удалить нельзя (`PROTECT`) — иначе пропали бы данные
  о подарках;
* события пользователя удаляются вместе с ним (`CASCADE`);
* при удалении подарка событие остаётся, но без подарка (`SET_NULL`).

`User` — модель предметной области, а не встроенный пользователь
`django.contrib.auth` (вход на сайт она не обеспечивает).

### Статусы подарка (`Gift.Status`, TextChoices)

`planned` — запланирован, `ordered` — заказан, `delivered` — вручён,
`cancelled` — отменён. Отменённый подарок **не удаляется**: запись
сохраняется для истории и статистики, но не учитывается как актуальная.

### Менеджер `GiftQuerySet`

`Gift.objects.active()` (все, кроме отменённых), `planned()`, `ordered()`,
`delivered()`, `cancelled()`, `for_date(day)`, `within_budget(sum)`,
`with_recipient()` (`select_related`), `search(text)`. Условия описаны один
раз и используются в представлениях, формах и статистике.

### Прочее

* `User.slug` формируется из имени транслитерацией («Мария» → `mariya`),
  страница получателя: `/recipients/<slug>/`, адрес даёт
  `User.get_absolute_url()` (используется и ссылкой «Смотреть на сайте»
  в админке).
* `Gift.total_cost` — `GeneratedField` (`price + delivery_cost`,
  `db_persist=True`): значение вычисляет и хранит сама база данных. После
  `save()` новое значение видно после `refresh_from_db()`.
* Контекстный процессор `gift_web/context_processors.py` передаёт во все
  шаблоны `site_name`, `current_year` и `active_gifts_count` (бейдж в меню).

## Миграции

| Миграция | Что делает |
|----------|------------|
| `0001_initial` | модели `User`, `Gift` (с `is_purchased`), `Event` — ПР9 |
| `0002_gift_status` | поле `status` |
| `0003_is_purchased_to_status` | миграция данных: `is_purchased` → `status` |
| `0004_remove_gift_is_purchased` | удаление старого поля |
| `0005_user_slug` | поле `slug`: добавление → заполнение → `unique` |
| `0006_gift_total_cost` | `GeneratedField total_cost` |
| `0007_gift_image` | `ImageField image` (ПР11) |

Данные переводятся в новый формат **до** удаления старого поля, поэтому
значения `is_purchased` не теряются.

## Страницы

| Адрес | Что показывает |
|-------|----------------|
| `/` | счётчики и три ближайших события |
| `/users/?q=` | пользователи, поиск по имени или e-mail |
| `/recipients/`, `/recipients/<slug>/` | получатели с числом и суммой актуальных подарков; подарки получателя |
| `/gifts/` | список подарков: форма фильтра (поиск, получатель, статус, период), сортировка, пагинация |
| `/gifts/new/`, `/gifts/<id>/edit/` | создание и редактирование (ModelForm, загрузка фото) |
| `/gifts/<id>/cancel/` | отмена подарка, **только POST** (GET → 405) |
| `/gifts/search/?budget=` | актуальные подарки в пределах бюджета |
| `/events/?date_from=&date_to=` | события за период |
| `/events/need-gift/` | предстоящие события без подарка или с отменённым подарком |
| `/statistics/` | сводка, статусы, группировка по получателям, порог числа подарков |
| `/admin/` | административная панель |

Несуществующий объект (`get_object_or_404`) → 404. Неверные параметры
(дата, сортировка, бюджет) не вызывают ошибку: форма показывает сообщение,
а список выводится без фильтра.

## ORM-запросы проекта (ПР9)

| Вид | Где | Выражение |
|-----|-----|-----------|
| Базовые | `index`, `gift_detail`, `recipient_detail` | `User.objects.count()`; `get_object_or_404(Gift.objects.select_related("recipient"), pk=...)`; `get_object_or_404(User, slug=...)` |
| Фильтрация | `gift_list` | `filter(status=...)`; `filter(recipient=...)` + `delivery_date__gte/__lte` (несколько условий) |
| Исключение | `GiftQuerySet.active()` | `exclude(status=Gift.Status.CANCELLED)` |
| По связанной модели | `events_need_gift` | `filter(Q(gift__isnull=True) \| Q(gift__status=CANCELLED))` |
| Поиск | `search()`, `user_list` | `name__icontains` / `recipient__name__icontains`; `name` или `email` |
| Сортировка | `gift_list`, `statistics` | `order_by(*SORT_FIELDS[sort])` (в т. ч. `recipient__name`); `order_by("-gifts_count", "name")` |
| Связи | `event_list`, `user_detail` | `select_related("user", "gift")`; обратная связь `user.events` |
| Только нужные поля | `gift_list` | `annotate(recipient_name=F("recipient__name"), status_label=Case(...)).values(...)` |
| Агрегирование | `statistics` | `aggregate(Count, Sum, Avg, Min, Max)`; `aggregate(Count("id", filter=Q(status=...)))` |
| Группировка | `statistics`, `recipient_list` | `values("status").annotate(Count, Sum)`; `User.objects.annotate(Count("gifts", filter=...), Sum(...))` |
| Аналог HAVING | `statistics` | `.filter(gifts_count__gte=min_gifts)` после `annotate` |
| Ограничение | `statistics`, `index` | `[:3]` (LIMIT) |
| Пагинация | `gift_list` | `Paginator(gifts, GIFTS_PER_PAGE)`, ссылки `{% querystring page=... %}` сохраняют фильтры |
| Проверка конфликта | `GiftForm.clean()` | `active().filter(recipient=...).for_date(...).exclude(pk=...).exists()` |
| Бюджет | `gift_search` | `active().within_budget(budget)` → `total_cost__lte` |

Сортировка задаётся только ключами словаря `SORT_FIELDS` (`forms.py`):
пользовательское значение не попадает в `order_by()` напрямую.

**Поиск кириллицы в SQLite.** SQLite сравнивает без учёта регистра только
латиницу, поэтому `icontains="иван"` не находит «Иван». Функция
`text_search_q()` ищет несколько вариантов написания (как введено,
строчными, с заглавной, прописными).

## Административная панель (ПР10)

* `User`: столбцы имя, e-mail, слаг, число подарков (`annotate`), поиск по
  имени и e-mail, слаг заполняется из имени (`prepopulated_fields`),
  inline-таблицы подарков и событий.
* `Gift`: столбцы включая `total_cost` и миниатюру фото, `list_editable` для
  статуса, фильтры по статусу, дате и получателю, `date_hierarchy`, поиск по
  названию и имени/e-mail получателя, `list_select_related`, действия
  «Отметить как заказанные» и «Отменить выбранные».
* `Event`: фильтры по дате и пользователю, поиск по названию, имени и подарку.
* Русские названия приложения (`GiftWebConfig.verbose_name`), моделей и полей
  (`verbose_name`), `LANGUAGE_CODE = "ru-ru"`.

Админ-панель не проверяет бизнес-правила формы сайта (например, конфликт
дат подарков) — эти проверки находятся в `GiftForm`.

**Django Debug Toolbar** подключается только при `DEBUG=True` и не в тестах
(`settings.py`), открывается кнопкой справа на страницах сайта; вкладка SQL
показывает запросы страницы.

## Формы (ПР11, `gift_web/forms.py`)

| Форма | Тип | Назначение |
|-------|-----|------------|
| `GiftFilterForm` | `forms.Form`, GET | поиск, получатель, статус, период, сортировка списка подарков |
| `BudgetForm` | `forms.Form`, GET | бюджет (`DecimalField`, `min_value=0`) |
| `EventPeriodForm` | `forms.Form`, GET | период событий |
| `GiftForm` | `ModelForm`, POST | создание подарка (без поля статуса) |
| `GiftEditForm` | `ModelForm`, POST | редактирование (+ статус, кроме «Отменён») |

Валидация:

* валидатор-функция `validate_not_only_digits` — название не из одних цифр;
* валидатор-класс `MaxFileSizeValidator(2)` — фото до 2 МБ;
* стандартный `MinValueValidator` — стоимость ≥ 1, доставка ≥ 0;
* `clean_delivery_date()` — дата доставки не в прошлом (при редактировании
  можно оставить прежнюю дату);
* `clean()` — доставка не дороже подарка; у получателя не может быть двух
  **актуальных** подарков на одну дату (отменённые не мешают, редактируемый
  подарок исключается через `exclude(pk=...)`);
* `GiftFilterForm.clean()` / `EventPeriodForm.clean()` — начало периода не
  позже конца.

Все POST-формы содержат `{% csrf_token %}`; отмена — отдельная POST-форма
(`@require_POST`). Фото сохраняются в `media/gifts/` (`MEDIA_ROOT`,
`MEDIA_URL`), форма отправляется с `enctype="multipart/form-data"`,
представление передаёт `request.FILES`. Нужен пакет Pillow.

## Структура проекта (актуальная)

```text
gift_project/settings.py     настройки (БД, медиа, Debug Toolbar, контекст)
gift_project/urls.py         корневые маршруты, /admin/, /media/, /__debug__/
gift_web/models.py           модели, GiftQuerySet, text_search_q
gift_web/forms.py            формы и валидаторы
gift_web/views.py            представления на ORM
gift_web/admin.py            настройка админ-панели
gift_web/context_processors.py
gift_web/slugs.py            транслитерация для слагов
gift_web/migrations/         миграции 0001–0007
gift_web/templates/          шаблоны (base.html, gift_form.html, includes/…)
gift_web/tests.py            тесты Django (модели, ORM, страницы, формы)
db/inspect_source_db.py      просмотр исходной базы ПР7
db/import_sqlite_to_orm.py   перенос данных ПР7 → ORM
pytest.ini, .flake8          настройки проверок
```
