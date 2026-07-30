# KanMind Backend

A RESTful backend for the **KanMind** Kanban board application, built with
Django and the Django REST Framework. It provides token-based authentication
and full CRUD access to boards, tasks and comments. This repository contains
the backend only — the frontend is a separate project.

## Features

- Token authentication (registration, login, email availability check)
- Boards with members, ownership and live counters
  (tickets, to-do tasks, high-priority tasks)
- Tasks with status, priority, assignee and reviewer
- "Assigned to me" and "Reviewing" task views
- Comments on tasks
- Object-level permissions (owner / member / author rules)
- Django admin for all resources

## Tech Stack

- Python 3.14
- Django 6.0
- Django REST Framework 3.17
- django-cors-headers
- SQLite (default development database)

## Getting Started

### 1. Clone the repository

```bash
git clone <repository-url>
cd KanMind
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv env
env\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv env
source env/bin/activate
```

### 3. Install the dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply the database migrations

```bash
python manage.py migrate
```

### 5. Create a superuser (for the admin panel)

```bash
python manage.py createsuperuser
```

### 6. Run the development server

```bash
python manage.py runserver
```

The API is now available at `http://127.0.0.1:8000/api/`
and the admin panel at `http://127.0.0.1:8000/admin/`.

## Connecting the Frontend

The frontend expects the API at `http://127.0.0.1:8000/api/`
(see `config.js` in the frontend project). CORS is enabled for all origins
during development, so the frontend can be served from the Live Server
extension without extra configuration.

## API Endpoints

All endpoints are prefixed with `/api/`. Except for registration and login,
every request must include an `Authorization: Token <token>` header.

### Authentication

| Method | Endpoint             | Description                    |
|--------|----------------------|--------------------------------|
| POST   | `/registration/`     | Register a new user            |
| POST   | `/login/`            | Log in and receive a token     |
| GET    | `/email-check/`      | Check whether an email exists  |

### Boards

| Method | Endpoint             | Description          |
|--------|----------------------|----------------------|
| GET    | `/boards/`           | List the user's boards |
| POST   | `/boards/`           | Create a board       |
| GET    | `/boards/{id}/`      | Retrieve a board     |
| PATCH  | `/boards/{id}/`      | Update a board       |
| DELETE | `/boards/{id}/`      | Delete a board (owner only) |

### Tasks

| Method | Endpoint                        | Description             |
|--------|----------------------------------|-------------------------|
| GET    | `/tasks/assigned-to-me/`         | Tasks assigned to you   |
| GET    | `/tasks/reviewing/`              | Tasks you review        |
| POST   | `/tasks/`                        | Create a task           |
| PATCH  | `/tasks/{id}/`                   | Update a task           |
| DELETE | `/tasks/{id}/`                   | Delete a task           |

### Comments

| Method | Endpoint                                   | Description        |
|--------|--------------------------------------------|--------------------|
| GET    | `/tasks/{task_id}/comments/`               | List comments      |
| POST   | `/tasks/{task_id}/comments/`               | Create a comment   |
| DELETE | `/tasks/{task_id}/comments/{comment_id}/`  | Delete a comment (author only) |

## Running the Tests

```bash
coverage run manage.py test
coverage report
```

The test suite covers all endpoints and permission rules with 100 % coverage.

## Project Structure

```
KanMind/
├── core/            # Project configuration (settings, root URLs)
├── auth_app/        # Authentication (registration, login, email check)
│   └── api/         # serializers, views, urls
├── kanban_app/      # Boards, tasks and comments
│   └── api/         # serializers, views, urls, permissions
├── manage.py
└── requirements.txt
```
