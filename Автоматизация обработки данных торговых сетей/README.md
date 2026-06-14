# 🏪 Автоматизация обработки данных торговой сети

Проект эмулирует ежедневную выгрузку данных с касс магазинов товаров для дома и автоматическую загрузку их в базу данных PostgreSQL.

---

## 🛠 Стек

- **Python** 3.8+
- **PostgreSQL** + DBeaver
- **Windows Task Scheduler** (планировщик)
- **pip**, **venv**

---

## 📁 Структура проекта

    .
    ├── config.py              # Все настройки (генерация + БД)
    ├── data_generator.py      # Генератор CSV-файлов с чеками
    ├── db_loader.py           # Загрузчик CSV в PostgreSQL
    ├── run_generator.bat      # Bat-файл (генерация)
    ├── run_loader.bat         # Bat-файл (загрузка в БД)
    ├── requirements.txt       # Python-зависимости
    ├── sql/
    │   └── create_tables.sql  # DDL таблицы checks
    ├── data/                  # Сгенерированные CSV
    ├── img/                   # Скриншоты для отчёта
    ├── logs.log               # Логи работы скриптов
    ├── .gitignore
    └── README.md

---

## ⚙️ Установка и запуск

### 1. Клонировать репозиторий

    git clone https://github.com/username/repository.git
    cd repository

### 2. Создать виртуальное окружение и активировать

    python -m venv venv
    venv\Scripts\activate      # Windows
    # source venv/bin/activate # macOS/Linux

### 3. Установить зависимости

    pip install -r requirements.txt

### 4. Настроить config.py

Открой `config.py` и укажи свои параметры подключения к PostgreSQL:

    DB_NAME = 'checks'
    DB_USER = 'postgres'
    DB_PASSWORD = 'твой_пароль'
    DB_HOST = 'localhost'
    DB_PORT = '5432'

### 5. Создать базу данных

Выполни SQL-скрипт из `sql/create_tables.sql` в DBeaver (или любом клиенте PostgreSQL). Будет создана таблица `checks`.

### 6. Запустить генерацию CSV

    python data_generator.py

Файлы появятся в папке `data/`.

### 7. Загрузить данные в БД

    python db_loader.py

Все строки из CSV попадут в таблицу `checks`.

---

## 🕐 Автоматизация (Windows)

Оба bat-файла заведены в **Планировщик заданий**:

| Задача | Bat-файл | Расписание |
|--------|----------|------------|
| Генерация CSV | `run_generator.bat` | Ежедневно, кроме воскресенья |
| Загрузка в БД | `run_loader.bat` | Ежедневно, кроме воскресенья (через 10 мин после генерации) |

Результаты запусков дописываются в `scheduler.log`. Подробные логи работы скриптов — в `logs.log`.
Примеры настройки планировщика находятся в папке [img/](img/)
Не забудь поменять самостоятельно пути в бат-файлах на свои


---

## 📊 Формат данных

### CSV (выгрузка кассы)

| Поле | Описание |
|------|----------|
| `doc_id` | Уникальный ID чека |
| `item` | Название товара |
| `category` | Категория (Бытовая химия, Текстиль, Посуда и др.) |
| `amount` | Количество единиц |
| `price` | Цена за 1 единицу |
| `discount` | Сумма скидки на позицию |

### Таблица `checks` (PostgreSQL)

| Поле | Тип | Ограничение |
|------|-----|-------------|
| `id` | `SERIAL` | `PRIMARY KEY` |
| `doc_id` | `VARCHAR(50)` | `NOT NULL` |
| `item` | `VARCHAR(200)` | `NOT NULL` |
| `category` | `VARCHAR(100)` | `NOT NULL` |
| `amount` | `INT` | `NOT NULL` |
| `price` | `NUMERIC(10,2)` | `NOT NULL` |
| `discount` | `NUMERIC(10,2)` | `DEFAULT 0` |

---

## 📸 Скриншоты

Все скриншоты находятся в папке `img/`:

- Структура таблицы `checks` в DBeaver
- Окно планировщика Windows с настроенными задачами
- Пример логов после выполнения генерации и загрузки

---

## 📬 Контакты

Выполнил: *AtacZy*