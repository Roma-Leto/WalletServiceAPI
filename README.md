# Wallet Service API

## Описание

Этот проект реализует API для управления кошельками с использованием FastAPI и PostgreSQL. 
Он позволяет создавать операции пополнения и снятия средств с кошельков, а также получать 
информацию о балансе кошелька.

Проект поддерживает высокую нагрузку (до 1000 запросов в секунду на один кошелек) и 
использует транзакции для обеспечения целостности данных в конкурентной среде.

## Стек технологий

- **FastAPI** — для создания API
- **SQLAlchemy** — для работы с базой данных
- **PostgreSQL** — для хранения данных
- **Liquibase** — для управления миграциями базы данных
- **Docker** и **Docker Compose** — для контейнеризации
- **pytest** и **httpx** — для тестирования

## Запуск проекта

### 1. Клонируйте репозиторий

```bash
git clone https://github.com/Roma-Leto/WalletServiceAPI.git
cd WalletServiceAPI
```

### 2. Соберите и запустите контейнеры с помощью Docker Compose

В корневой директории проекта выполните следующую команду:

```bash
docker-compose up --build
```

Это создаст и запустит два контейнера:
- Один для приложения на FastAPI
- Один для базы данных PostgreSQL

После этого приложение будет доступно по адресу `http://localhost:8000`.

### 3. Миграции базы данных

Проект использует Liquibase для управления миграциями базы данных. Миграции могут быть выполнены при запуске контейнера или вручную, если необходимо.

### 4. Настройки приложения

Конфигурация базы данных и другие параметры могут быть изменены через переменные окружения, указанные в файле `.env`.

Пример файла `.env`:

```ini
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=wallet_db
DATABASE_URL=postgresql+asyncpg://postgres:password@db/wallet_db
```

### 5. Тестирование

Для тестирования API используется библиотека `pytest` в связке с `httpx` для асинхронных HTTP-запросов.

Для запуска тестов выполните команду:

```bash
pytest
```

Тесты проверяют основные эндпоинты, включая создание операции и получение баланса кошелька.

## Эндпоинты API

### POST `/api/v1/wallets/{wallet_uuid}/operation`

**Описание**: Создание операции пополнения или снятия средств с кошелька.

**Тело запроса**:

```json
{
    "operationType": "DEPOSIT" | "WITHDRAW",
    "amount": <int>
}
```

**Ответ**:

```json
{
    "status": "success",
    "transaction": {
        "uuid": "<wallet_uuid>",
        "balance": <current_balance>
    }
}
```

**Пример**:

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/wallets/test_wallet/operation' \
  -H 'Content-Type: application/json' \
  -d '{
  "operationType": "DEPOSIT",
  "amount": 1000
}'
```

### GET `/api/v1/wallets/{wallet_uuid}`

**Описание**: Получение баланса кошелька.

**Ответ**:

```json
{
    "uuid": "<wallet_uuid>",
    "balance": <current_balance>
}
```

**Пример**:

```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/wallets/test_wallet'
```

### Обработка ошибок

Приложение обрабатывает следующие типы ошибок:

- **404 Not Found** — кошелек не найден.
- **400 Bad Request** — некорректный запрос (например, неверный формат JSON или 
неправильный тип операции).
- **500 Internal Server Error** — ошибка на стороне сервера (например, ошибка базы данных).

## Структура проекта

```
.
├── app/
│   ├── __init__.py
│   ├── main.py          # Основной файл FastAPI
│   ├── models.py        # Модели для базы данных (SQLAlchemy)
│   ├── crud.py          # CRUD-операции для работы с базой данных
│   ├── database.py      # Настройки подключения к базе данных
├── migrations/          # Миграции Liquibase
│   └── changelog.xml
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Лицензия

Этот проект лицензирован под [MIT License](LICENSE).

## Контрибьюции

Если вы хотите внести свой вклад в этот проект, пожалуйста, откройте issue или создайте 
pull request. Ваши улучшения и исправления будут приветствоваться!