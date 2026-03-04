# Sunday School Students Profile Management System (SS-SPMS)

Ethiopian Orthodox Tewahedo Church (EOTC) — Single Parish Installation (MVP v1)

## Overview
SS-SPMS is a profile management and attendance tracking system designed for EOTC parishes. It handles student registrations, attendance, Mezemran membership, and reporting.

## Tech Stack
- **Backend**: Django 5.x (Python 3.12+)
- **Frontend**: Django Templates + HTMX + Tailwind CSS
- **Database**: PostgreSQL 16+
- **PDF Generation**: ReportLab
- **Ethiopian Calendar**: ethioqen

## Quickstart (Development)
1. Clone the repository.
2. Copy `.env.example` to `.env` and fill in the values.
3. Run `docker compose up --build`.
4. Run migrations: `docker compose exec web python manage.py migrate`.
5. Create a superuser: `docker compose exec web python manage.py createsuperuser`.

## Running Tests
Run tests using the provided script:
```bash
./scripts/test.sh
```
Or directly via docker compose:
```bash
docker compose exec web python -m pytest
```

## CI/CD
Automated testing and linting are performed on every Pull Request via GitHub Actions.
- **Linter**: Ruff
- **Formatter**: Black
- **Tests**: Pytest