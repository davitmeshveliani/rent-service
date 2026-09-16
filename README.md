
# Rentify

Rentify is a backend REST API for a real estate listing and booking platform.

The project provides user authentication, property listings, reservations, reviews, filtering, validation,
    Docker-based development, automated tests, and deployment support for a Linux/AWS environment.

Rentify — это backend REST API для платформы аренды недвижимости.

Проект включает регистрацию и аутентификацию пользователей, объявления о недвижимости, бронирование, отзывы,
    фильтрацию, валидацию, Docker-окружение, тестирование и возможность развёртывания на Linux/AWS сервере.


## Technologies / Технологии

- Python
- Django
- Django REST Framework
- MySQL
- Docker
- Docker Compose
- Nginx
- JWT Authentication
- HttpOnly Cookies
- drf-spectacular / Swagger
- django-filter
- django-simple-history
- pytest-style Django test suite / Django Test Framework


## Main Features / Основные возможности

### Users / Пользователи

- User registration and authentication
- Email and username validation
- Password validation
- JWT authentication
- HttpOnly access and refresh cookies
- User profile management
- User roles:
  - Guest
  - Host
  - Both

### Listings / Объявления

- Create, read, update and delete listings
- Host-based ownership
- Property information and pricing
- Property images
- Search
- Filtering by:
  - price
  - rooms
  - city
  - district
  - property type
- Sorting by price and dates
- Listing view tracking

### Reservations / Бронирование

- Create reservations
- Reservation status management
- Confirm and reject reservations
- Reservation cancellation
- Protection against overlapping reservations
- Protection against invalid dates
- Booking dates cannot be in the past
- Booking start date is limited to one year in advance
- Users cannot create reservations for their own listings

### Reviews / Отзывы

- Reviews are available after an eligible completed stay
- Review validation is connected to reservation status
- Users cannot create invalid reviews for unrelated reservations


## API Endpoints / Основные маршруты

The following routes provide a quick overview of the main API functionality.

Следующие маршруты дают краткий обзор основных возможностей API.

### Authentication / Аутентификация

- `POST /api/auth/register/` — register a new user
- `POST /api/auth/login/` — login and receive JWT cookies
- `POST /api/auth/refresh/` — refresh authentication tokens

### Users / Пользователи

- `GET /api/users/me/` — get the current user's profile
- `PATCH /api/users/me/` — update the current user's profile

### Listings / Объявления

- `GET /api/listings/` — list available properties
- `POST /api/listings/` — create a new listing
- `GET /api/listings/{id}/` — get listing details
- `PATCH /api/listings/{id}/` — update a listing
- `DELETE /api/listings/{id}/` — delete a listing

Listings support search, filtering and ordering.

### Reservations / Бронирование

- `GET /api/reservations/` — list reservations available to the authenticated user
- `POST /api/reservations/` — create a reservation
- `GET /api/reservations/{id}/` — get reservation details
- `PATCH /api/reservations/{id}/` — update reservation information
- `DELETE /api/reservations/{id}/` — cancel/delete a reservation according to the API rules

### Reviews / Отзывы

- `GET /api/reviews/` — list reviews
- `POST /api/reviews/` — create a review
- `GET /api/reviews/{id}/` — get review details
- `PATCH /api/reviews/{id}/` — update a review
- `DELETE /api/reviews/{id}/` — delete a review

### API Documentation / Документация API

- `GET /api/docs/` — Swagger UI
- `GET /api/schema/` — OpenAPI schema


# Installation & Running / Установка и запуск

The project can be run locally with Docker and deployed to a Linux/AWS EC2 server.

Проект можно запускать локально через Docker и разворачивать на Linux/AWS EC2 сервере.


## 1. Clone the Repository / Клонирование репозитория

Clone the project from GitHub:

    git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
    cd YOUR_REPOSITORY

Replace `YOUR_USERNAME/YOUR_REPOSITORY` with the actual GitHub repository.


## 2. Configure Environment Variables / Настройка переменных окружения

The project uses environment variables for configuration and sensitive information.

Проект использует переменные окружения для настроек и секретных данных.

Create a `.env` file in the project root:

    SECRET_KEY=your-secret-key
    DEBUG=False

    DB_ENGINE=django.db.backends.mysql
    DB_NAME=rentify_db
    DB_USER=rentify_user
    DB_PASSWORD=your-password
    DB_HOST=db
    DB_PORT=3306

    EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
    DEFAULT_FROM_EMAIL=noreply@rentify.local

Use secure production values on the server.

Для production-сервера необходимо использовать собственные безопасные значения.


### Important Security Rule / Важное правило безопасности

The `.env` file must NOT be committed to GitHub.

Файл `.env` НЕ должен загружаться в GitHub.

Add it to `.gitignore`:

    .env

The production `.env` file should be created directly on the server and should remain outside the Git repository.


# Local Development with Docker / Локальный запуск через Docker

Make sure Docker Desktop is installed and running.

Убедитесь, что Docker Desktop установлен и запущен.


## 3. Start Docker Containers / Запуск Docker-контейнеров

From the project root:

    docker compose up -d

Check the containers:

    docker compose ps

The project uses Docker services for the application, database and Nginx.


## 4. Apply Database Migrations / Применение миграций

Run:

    docker compose exec web python manage.py migrate

This applies all Django database migrations.

Эта команда применяет все миграции Django к базе данных.


## 5. Create an Admin User / Создание администратора

This step is optional.

Этот шаг необязательный.

Run:

    docker compose exec web python manage.py createsuperuser

Follow the prompts to create an administrator account.


## 6. Collect Static Files / Сбор статических файлов

Run:

    docker compose exec web python manage.py collectstatic --noinput

This prepares static files for serving through the configured web server.


## 7. Open Swagger / Открыть Swagger

After the containers are running, open:

    http://localhost:8081/api/docs/

Swagger provides interactive API documentation and allows the available endpoints to be tested directly from the browser.


## 8. Run Tests / Запуск тестов

Run the Django test suite inside the web container:

    docker compose exec web python manage.py test

The project contains tests covering important user, listing and reservation behavior.


# Server Deployment / Развёртывание на сервере

The application can be deployed to a Linux server such as AWS EC2.

Приложение можно развернуть на Linux-сервере, например AWS EC2.

The server should have:

- Linux
- Docker
- Docker Compose
- Git


## 9. Clone the Repository on the Server / Клонирование на сервере

Connect to the server and clone the repository:

    git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
    cd YOUR_REPOSITORY


## 10. Create the Production .env / Создание production .env

Create the environment file directly on the server:

    nano .env

Example:

    SECRET_KEY=your-production-secret-key
    DEBUG=False

    DB_ENGINE=django.db.backends.mysql
    DB_NAME=rentify_db
    DB_USER=rentify_user
    DB_PASSWORD=your-production-password
    DB_HOST=db
    DB_PORT=3306

    EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
    DEFAULT_FROM_EMAIL=your-email@example.com

Production credentials and secrets should be stored only on the server.

Production `.env` должен храниться только на сервере и не должен попадать в GitHub.


## 11. Build and Start the Application / Сборка и запуск приложения

Run:

    docker compose up -d --build

Check the running containers:

    docker compose ps


## 12. Apply Migrations on the Server / Миграции на сервере

Run:

    docker compose exec web python manage.py migrate

Then collect static files:

    docker compose exec web python manage.py collectstatic --noinput


# Updating the Server / Обновление сервера

When a new version is pushed to GitHub, update the server with:

    git pull

Then rebuild and restart the application:

    docker compose up -d --build

Check the containers:

    docker compose ps

The server `.env` file remains on the server and is not replaced by the Git repository.


# Authentication / Аутентификация

Rentify uses JWT-based authentication with HttpOnly cookies.

The authentication system includes:

- Access token
- Refresh token
- HttpOnly cookies
- Protected API endpoints
- CSRF protection for cookie-based authentication

HttpOnly cookies prevent client-side JavaScript from directly accessing the authentication tokens.

Для аутентификации используются JWT-токены, хранящиеся в HttpOnly cookies.


# API Documentation / Документация API

Swagger UI is provided through drf-spectacular.

Local Swagger:

    http://localhost:8081/api/docs/

Swagger provides interactive documentation for the REST API and allows developers to inspect and test available endpoints.


# Security / Безопасность

The project follows several basic security practices:

- Sensitive configuration is stored in environment variables
- `.env` is excluded from Git
- JWT tokens are stored in HttpOnly cookies
- Password validation is enabled
- Protected endpoints require authentication
- User permissions are checked for protected operations
- Production secrets are stored directly on the server
- HTTPS should be used in production


# Project Structure / Структура проекта

The main Django applications are organized by responsibility:

- `core` — core project functionality
- `users` — users, authentication and profiles
- `listings` — real estate listings and related functionality
- `reservations` — booking and reservation logic
- `reviews` — reviews and rating-related functionality

The project also contains Docker, Nginx, database and configuration files required for local development and deployment.


# Project Status / Статус проекта

Rentify is a completed backend REST API project demonstrating:

- Django and Django REST Framework
- REST API architecture
- JWT authentication
- HttpOnly cookie authentication
- MySQL database integration
- Property listing management
- Reservation management
- Review functionality
- Search, filtering and ordering
- Data validation and business rules
- Automated testing
- Docker and Docker Compose
- Nginx
- Linux/AWS server deployment
- API documentation with Swagger

The project is structured as a portfolio backend project demonstrating practical development,
            testing, containerization and deployment skills.

