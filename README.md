# Corporate Microblog

Бэкенд корпоративного сервиса микроблогов на FastAPI и PostgreSQL.

## Возможности

- Создание и удаление собственных твитов
- Загрузка изображений и прикрепление их к твитам
- Лайки и снятие лайков
- Подписки и отписки
- Лента твитов пользователей, на которых подписан текущий пользователь
- Профили пользователей
- Swagger-документация
- Хранение данных в PostgreSQL
- Запуск через Docker Compose

## Быстрый старт

```bash
docker compose up -d
```

После запуска откройте:

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json

## Демо-ключи

| Пользователь | api-key |
|---|---|
| Alice | `test-key-alice` |
| Bob | `test-key-bob` |
| Carol | `test-key-carol` |

## Пример создания твита

```bash
curl -X POST http://localhost:8000/api/tweets \
  -H "api-key: test-key-alice" \
  -H "Content-Type: application/json" \
  -d '{"tweet_data": "Первый твит", "tweet_media_ids": []}'
```

## Пример загрузки изображения

```bash
curl -X POST http://localhost:8000/api/medias \
  -H "api-key: test-key-alice" \
  -F "file=@image.jpg"
```

## Тесты и линтер

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest --cov=app
ruff check .
mypy app
```

## Остановка

```bash
docker compose down
```

Данные PostgreSQL сохраняются в Docker volume `postgres_data`.