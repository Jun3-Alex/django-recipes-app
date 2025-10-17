# django-recipes-app

Этот репозиторий содержит Django‑приложение для управления и публикации рецептов. Проект включает контейнеризованный сценарий развёртывания с использованием Docker, Gunicorn, PostgreSQL и прокси-сервера Nginx на хосте.

## Предварительные требования

- Docker Engine 24+
- Docker Compose V2
- GNU Make (необязательно, но удобно)

## Настройка окружения

1. Скопируйте пример файла окружения и заполните значения под своё развёртывание:

   ```bash
   cp .env.example .env
   ```

2. Укажите секреты и параметры базы данных в `.env`:

   - `DJANGO_SECRET_KEY`: длинная случайная строка для Django.
   - `DJANGO_DEBUG`: `False` для продакшена, `True` для локальной отладки.
   - `ALLOWED_HOSTS`: список хостов через запятую, которые будет обслуживать Nginx.
   - `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`: учётные данные PostgreSQL контейнера. Эти ключи используются для сборки настроек Django; если их удалить, проект автоматически вернётся к SQLite (удобно для локальной разработки без Postgres).
   - `DATABASE_URL`: полноценная строка подключения Postgres для Django и внешних инструментов. При наличии перекрывает параметры `DB_*`.

## Сборка контейнеров

Соберите Docker-образы, описанные в `infra/`:

```bash
docker compose -f infra/docker-compose.yml --env-file .env build
```

## Запуск стека

Поднимите сервисы web и db в приватной сети Docker:

```bash
docker compose -f infra/docker-compose.yml --env-file .env up -d
```

Gunicorn доступен только по адресу `127.0.0.1:8000`. Для публикации приложения наружу используйте Nginx на хосте (см. ниже).

Проверка статуса контейнеров:

```bash
docker compose -f infra/docker-compose.yml ps
```

Остановка стека:

```bash
docker compose -f infra/docker-compose.yml down
```

## Миграции базы данных

После запуска контейнеров примените миграции (они выполняются против контейнера PostgreSQL и сохраняют состояние в томе `postgres_data`, поэтому перезапуск сервисов не удалит данные):

```bash
docker compose -f infra/docker-compose.yml exec web python manage.py migrate
```

Откат последней миграции для всех приложений:

```bash
docker compose -f infra/docker-compose.yml exec web python manage.py migrate --plan
# изучите план, затем выполните откат конкретного приложения, например:
docker compose -f infra/docker-compose.yml exec web python manage.py migrate recipes zero
```

Для точечных откатов выполняйте миграции в обратном порядке или восстановите базу данных из резервной копии.

## Статические файлы

Соберите статические файлы в общую директорию перед выдачей трафика:

```bash
docker compose -f infra/docker-compose.yml exec web python manage.py collectstatic --noinput
```

Том `staticfiles` монтируется в `/app/app/staticfiles` внутри контейнера и должен обслуживаться Nginx.

## Создание суперпользователя

Создайте административного пользователя для доступа к Django Admin:

```bash
docker compose -f infra/docker-compose.yml exec web python manage.py createsuperuser
```

## Засев тестовыми рецептами

Заполните базу примерными данными для демонстраций или тестирования:

```bash
docker compose -f infra/docker-compose.yml exec web python manage.py seed_recipes
```

Команду можно запускать повторно, чтобы обновить набор данных.

## Конфигурация Nginx на хосте

Каталог `infra/nginx/` намеренно оставлен пустым и предназначен для бинда настроек Nginx, если вы решите запускать его в Docker. При использовании Nginx на хосте создайте конфигурацию сайта по аналогии:

```nginx
upstream django_recipes_app {
    server 127.0.0.1:8000 fail_timeout=0;
}

server {
    listen 80;
    server_name recipes.example.com;

    location /static/ {
        alias /var/www/django-recipes-app/staticfiles/;
    }

    location /media/ {
        alias /var/www/django-recipes-app/media/;
    }

    location / {
        proxy_pass http://django_recipes_app;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Скорректируйте пути к файловой системе под расположение статических и медиадиректорий на хосте.

## Чек-лист обслуживания и отката

1. Остановите пользовательский трафик на балансировщике или включите режим обслуживания.
2. Создайте резервную копию базы PostgreSQL:

   ```bash
   docker compose -f infra/docker-compose.yml exec db pg_dump -U "$DB_USER" "$DB_NAME" > backup.sql
   ```

3. Задеплойте обновления (обновите код, пересоберите образ `web`, перезапустите контейнеры).
4. Примените миграции и соберите статику, как показано выше.
5. Выполните смоук-тесты или проверки здоровья.
6. Если возникли проблемы:
   - Восстановите базу данных из резервной копии.
   - Пересоберите и задеплойте предыдущий тег Docker-образа.
   - Откатите миграции (см. пример выше).
   - Верните трафик после проверки работоспособности.

Следуя этому чек-листу, вы сможете безопасно разворачивать и откатывать приложение с минимальным простоем.