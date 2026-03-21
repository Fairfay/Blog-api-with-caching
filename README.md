# Blog API with caching

REST API for blog posts with PostgreSQL persistence, Redis cache for the detail endpoint, and an integration test for cache behavior.

## Implemented

- CRUD for posts
- cache-aside strategy for `GET /api/v1/posts/{id}`
- cache invalidation on update and delete
- integration tests for cache warmup, cache hits, and invalidation

## Stack

- Django 6
- Django REST Framework
- PostgreSQL
- Redis
- Poetry
- Docker Compose

## API endpoints

- `POST /api/v1/posts`
- `GET /api/v1/posts`
- `GET /api/v1/posts/{id}`
- `PATCH /api/v1/posts/{id}`
- `PUT /api/v1/posts/{id}`
- `DELETE /api/v1/posts/{id}`

## Architecture

See [docs/architecture.md](docs/architecture.md).

## Why this cache approach

The project uses cache-aside:

- a post is loaded from Redis first
- on cache miss the API reads it from PostgreSQL and stores the serialized payload in Redis
- on update or delete the cache key is removed

This keeps the implementation simple, predictable, and a good fit for popular posts because the most frequently requested records naturally stay hot in Redis.

## Environment variables

1. Create `.env` from `.env.template`.
2. Adjust values if needed.

Important variables:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `REDIS_URL`
- `POST_CACHE_TIMEOUT`

Default local ports in the provided `.env`:

- PostgreSQL: `55432`
- Redis: `56379`

## Local run with Poetry

1. Install dependencies:

```bash
poetry install
```

2. Start PostgreSQL and Redis:

```bash
docker compose up -d db redis
```

3. Apply migrations:

```bash
poetry run python manage.py migrate
```

4. Run the API:

```bash
poetry run python manage.py runserver
```

## Run with Docker Compose

```bash
docker compose up --build
```

The API will be available at `http://127.0.0.1:8000/api/v1/posts`.

## Run tests

Start PostgreSQL and Redis first:

```bash
docker compose up -d db redis
```

Then run:

```bash
poetry run python manage.py test
```
