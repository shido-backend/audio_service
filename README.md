# 🎵 Audio Service API

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)

Сервис для загрузки и управления аудиофайлами с безопасной авторизацией через Яндекс OAuth.

## 🌟 Особенности

- 🔐 Авторизация через Яндекс OAuth 2.0
- 🎧 Загрузка и скачивание аудиофайлов
- 📝 Назначение пользовательских имен файлам
- 🛡️ JWT-аутентификация для API
- 🐳 Готовая Docker-конфигурация
- 📊 Полная документация API (ReDoc)

## 🚀 Быстрый старт

### Предварительные требования

- Docker 20.10+
- Docker Compose 1.29+

### Установка

1. Клонируйте репозиторий:

```bash
git clone https://github.com/yourusername/audio-service.git
cd audio-service
```

2. Настройте окружение

```bash
cp .env.example .env
```

3. Укажите нужные данные в .env

```bash
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
POSTGRES_HOST=
POSTGRES_PORT=

# Yandex OAuth (получить на https://oauth.yandex.ru/)
YANDEX_CLIENT_ID=
YANDEX_CLIENT_SECRET=
YANDEX_REDIRECT_URI

# JWT Settings
JWT_SECRET=сложная_секретная_строка_минимум_32_символа
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# FILES
AUDIO_UPLOAD_DIR=media/audio_files
CREATE_STORAGE_DIRS=true
```

4. Запустите сервис.

```bash
docker-compose up --build -d
```

Сервис будет доступен по адресу: http://localhost:8000

### 📚 Документация API

После запуска доступны:

ReDoc: http://localhost:8000/api/redoc

OpenAPI Schema: http://localhost:8000/api/openapi.json

### 🛠️ Основные эндпоинты

Метод	Путь	                    Описание
GET	    /api/auth/yandex-login	    Инициировать авторизацию через Яндекс
GET	    /api/auth/yandex-callback	Callback для Яндекс OAuth
POST	/api/auth/register	        Регистрация нового пользователя
POST	/api/auth/login	            Логин с email/паролем
GET	    /api/auth/me	            Информация о текущем пользователе
POST	/api/audio/upload	        Загрузка аудиофайла
GET	    /api/audio/me	            Получить список аудио пользователя
GET	    /api/audio/download/{id}	Скачать аудиофайл

### 🐳 Docker Конфигурация

Сервис состоит из двух контейнеров:

app - FastAPI приложение

Порт: 8000

Автоматическая перезагрузка при изменениях кода

Хранилище аудио: /app/audio_uploads

db - PostgreSQL 16

Порт: 5432

Данные сохраняются в volume

### 🔄 Миграции базы данных

При первом запуске автоматически создаются таблицы. Для ручного управления миграциями:

```bash
docker-compose exec app alembic upgrade head
```

## 🛠️ Технологический стек

Backend: FastAPI (Python 3.11)

База данных: PostgreSQL 16

Аутентификация: Яндекс OAuth + JWT

Хранилище файлов: Локальная файловая система

Контейнеризация: Docker + Docker Compose
