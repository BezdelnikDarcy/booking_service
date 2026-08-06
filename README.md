<div align="center">

# ✂️ Beauty Booking Service

## Описание проекта

</div>

Beauty Booking Service — серверное REST-приложение для автоматизации работы салона красоты. Система предоставляет единое API для клиентов, мастеров и администраторов, позволяя управлять расписанием сотрудников, услугами, бронированиями, отзывами, уведомлениями и внутренними процессами салона.

---

<div align="center">

# 🛠️Используемые технологии


![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-6.0-092E20?logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/Django_REST_Framework-API-A30000)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-4169E1?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-5.6-37814A?logo=celery&logoColor=white)
![Flower](https://img.shields.io/pypi/v/flower?color=37814A&label=Flower&style=flat-square)
![django-selery-beat](https://img.shields.io/pypi/v/django-celery-beat?color=37814A&label=django-selery-beat&style=flat-square)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)
![Pillow](https://img.shields.io/pypi/v/pillow?label=Pillow)
[![API Docs](https://img.shields.io/badge/API_Docs-Swagger-85EA2D?logo=swagger&logoColor=black)](http://localhost:8000/api/schema/swagger-ui/)


---


# 🏗️ Структура проекта

Проект разделён на независимые приложения Django.

</div>

```text
src
│
├── account
│     Пользователи, авторизация и роли системы
│
├── booking_manager
│     Основная бизнес-логика проекта
│     ├── models          Модели базы данных
│     ├── services        Сервисный слой
│     ├── v1              REST API
│     │     ├── serializers     Сериализаторы
│     │     ├── filters         Фильтрация данных
│     │     └── views           API router
│     ├── tasks           Celery-задачи
│     └── admin           Панель администратора
│
├── config
│     Настройки Django, Celery, Redis и JWT
│
└── manage.py
```
# Архитектура

```text
Client
   │
HTTP Request
   │
REST API (ViewSet)
   │
Serializer
   │
Service Layer
   │
Models
   │
PostgreSQL

          │
      Celery + Redis
          │
      Notifications
```
# Основные сущности базы данных
- Users
- Categories
- Services
- Bookings
- Reviews
- Notifications
- EmployeeServices
- PromoCodes
- EmployeeSchedule
- SalonSchedule
- EmployeeDayOff
- PromoUsage

### Реализованный функционал

- 🔐 JWT-аутентификация и авторизация
- 👥 Роли пользователей
- 🏢 Управление расписанием салона
- ✂️ Каталог услуг
- 💇 Управление мастерами
- 📅 Онлайн-бронирование
- ⭐ Система отзывов и рейтингов мастеров
- 🔔 Уведомления
- ⚙️ Celery + Redis
- 🐳 Docker Compose


---
<div align="center">

# 🚀 Запуск проекта

</div>

## 1. Клонирование репозитория

```bash
git clone https://github.com/BezdelnikDarcy/booking_service.git
cd booking_service
```

---

## 2. Создание файла окружения

Создать файл `.env` в корне проекта.

Скопируйте шаблон окружения или вручную создайте файл на основе `.env.example`

```bash
cp .env.example .env
```


---

## 3. Запуск Docker Compose

```bash
docker compose up --build
```

При первом запуске будут автоматически созданы контейнеры:

- PostgreSQL
- Redis
- Django
- Celery Worker
- Celery Beat
- Flower

---

## 4. Применение миграций

После запуска контейнеров выполнить:

```bash
docker compose exec web python manage.py migrate
```

---

## 5. Создание администратора

```bash
docker compose exec web python manage.py createsuperuser
```

---

## 6. Доступ к приложению

Django Admin

```
http://localhost:8000/admin/
```

Flower

```
http://localhost:5555/
```

---

# Запуск без Docker

Создать виртуальное окружение:

```bash
python -m venv .venv
```

Активировать окружение.

Windows

```bash
.venv\Scripts\activate
```

Linux

```bash
source .venv/bin/activate
```

Установить зависимости:

```bash
pip install -r requirements.txt
```

Создать файл `.env`.

В этом случае необходимо изменить

```env
PG_HOST=localhost
```

Применить миграции:

```bash
python manage.py migrate
```

Создать администратора:

```bash
python manage.py createsuperuser
```

Запустить сервер:

```bash
python manage.py runserver
```

---

# 🐳 Используемые сервисы с используемыми портами в Docker

| Сервис       | Порт  |
|--------------|:-----:|
| Django       | 8000  |
| PostgreSQL   | 5433  |
| Redis        | 6380  |
| celery_worker |   -   |
| celery_beat  |   -   |
| Flower       | 5555  |

___
# Заключение

Проект демонстрирует разработку современного серверного приложения с использованием Django REST Framework, PostgreSQL, Celery, Redis и Docker.

В процессе разработки были реализованы:

- REST API;
- ролевая модель пользователей;
- система онлайн-бронирования;
- управление расписанием сотрудников;
- сервисный слой бизнес-логики;
- асинхронная обработка задач;
- контейнеризация приложения.

Проект может служить основой для дальнейшего развития полноценной системы автоматизации салона красоты.
