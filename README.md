# Streetfix

Streetfix is a Django CMS foundation for street reporting. It includes public
reporting and staff-facing app areas, Django Admin management, and configurable
site branding and theme settings.

> **Project status:** The project is under active development. The intake,
> employee, and analytics pages are currently landing-page scaffolds; the
> public report form and dashboard workflows are not yet implemented. The data
> models and Django Admin provide a starting point for building those
> workflows.

## Features

- **Site branding and theme:** Administrators can configure the site name,
  favicon, navbar icon, and color tokens in Django Admin. Theme colors are
  validated for WCAG AA text contrast. Favicon uploads use Cloudinary.
- **Reporting and work data models:** The `intake` and `employees` apps define
  report submissions, work items, organizations, work status history, and
  related lookup values. Migrations create the initial fixed lookup values.
- **Django Admin:** Manage the available data and theme settings at `/admin/`.
  Some lookup codes and history records are intentionally read-only.
- **Static assets:** UIkit and the site theme are served from the project's
  static files; WhiteNoise supports serving collected static files in
  production.

## Tech stack

- Python `>=3.14,<3.15`
- Django 6.1
- `uv` for dependency management (`pyproject.toml` and `uv.lock`)
- SQLite for the example local database; PostgreSQL is supported for
  production
- pytest, Ruff, mypy, and pre-commit for testing and code quality

## Getting started

### Prerequisites

Install Python 3.14 and [uv](https://docs.astral.sh/uv/).

### Install and configure

From the repository root, install the locked dependencies:

```shell
uv sync --locked
```

Create a local environment file from the example:

```powershell
Copy-Item .env.example .env
```

On macOS or Linux, use `cp .env.example .env` instead. Edit `.env` and replace
the example `DJANGO_SECRET_KEY` with a development-only secret. The example
`DATABASE_URL=sqlite:///db.sqlite3` uses a local SQLite database. The local
database file is ignored by Git.

Cloudinary is only needed to upload a favicon. Set `CLOUDINARY_URL` to
credentials for your Cloudinary account before using that feature; the rest of
the local app can be explored without uploading a favicon.

### Create the database and admin account

Apply migrations, which also add the initial fixed reporting and work lookup
values:

```shell
uv run python manage.py migrate
uv run python manage.py createsuperuser
```

Start the development server:

```shell
uv run python manage.py runserver
```

Open <http://127.0.0.1:8000/> for the site or
<http://127.0.0.1:8000/admin/> to sign in to Django Admin. To configure the
site branding and theme, create the single **Theme settings** record in Admin
if it does not exist, then edit its fields.

### Local environment variables

Development settings load `.env`. These variables are required to start the
development app:

| Variable | Purpose |
| --- | --- |
| `DJANGO_SECRET_KEY` | Django signing key; use a private, local-only value for development. |
| `DATABASE_URL` | Database connection URL. The example selects SQLite at `db.sqlite3`. |
| `DJANGO_SETTINGS_MODULE` | Settings module. The example selects `config.settings.development`; `manage.py` uses it by default. |

`CLOUDINARY_URL` is optional for general local development and is needed to
upload a favicon through the theme settings.

Development settings provide local `ALLOWED_HOSTS` and
`CSRF_TRUSTED_ORIGINS` defaults. Do not commit `.env` or production credentials.

## Application routes

| Path | Area | Current status |
| --- | --- | --- |
| `/` | Public intake | Landing page; the submission workflow is not implemented yet. |
| `/employees/` | Employee workspace | Dashboard scaffold. |
| `/analytics/` | Analytics | Overview scaffold. |
| `/admin/` | Django Admin | Data and site-settings administration. |

## Project layout

| Path | Responsibility |
| --- | --- |
| `config/` | Django URL routing, ASGI/WSGI entry points, and settings modules. |
| `intake/` | Public reporting and report-submission models. |
| `employees/` | Departments, employees, work items, lifecycle, and work options. |
| `analytics/` | Analytics app and overview page scaffold. |
| `site_settings/` | Site branding, theme model, and template context processor. |
| `templates/` | Shared base template and app page templates. |
| `static/` | Source CSS, JavaScript, and UIkit assets. |
| `tests/` | pytest tests organized by app. |

## Tests and code quality

The test settings use SQLite. `DJANGO_SECRET_KEY` and `DATABASE_URL` still need
to be set (for example, in `.env`) because the test settings import the
development settings.

Run the test suite:

```shell
uv run pytest
```

Run the same core checks used by CI:

```shell
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run python manage.py collectstatic --noinput
```

Pre-commit hooks are configured for branch protection, Ruff, and Django
templates. Run them with:

```shell
uv run pre-commit run --all-files
```

## Production and deployment notes

Production uses `config.settings.production`, PostgreSQL-style `DATABASE_URL`,
and HTTPS-aware security settings. Configure these environment variables in
the hosting environment:

- `DJANGO_SETTINGS_MODULE=config.settings.production`
- `DJANGO_SECRET_KEY`
- `DATABASE_URL` (the production database connection must support SSL)
- `ALLOWED_HOSTS` (comma-separated hostnames without a scheme)
- `CSRF_TRUSTED_ORIGINS` (comma-separated origins including `https://`)
- `CLOUDINARY_URL` to enable favicon uploads

Collect static files with `uv run python manage.py collectstatic --noinput`.
The WSGI application is `config.wsgi:application` and can be served with
Gunicorn, for example:

```shell
uv run gunicorn config.wsgi:application
```

The GitHub Actions workflow on pushes to `main` runs database migrations; it
does not build or deploy the application. Hosting and release steps must be
configured separately.

## Repository conventions and automation

This project inherits the repository governance and automation from its base
template:

- [CONVENTIONS.md](CONVENTIONS.md) describes branch names, Conventional
  Commits, pull requests, and merge strategy.
- GitHub issue and pull request templates are available under `.github/`.
- GitHub Actions synchronizes labels from `.github/labels.yml`.
- Dependabot is configured for weekly GitHub Actions, `uv`, and npm dependency
  updates.
- CI runs Ruff, mypy, migrations, static collection, and pytest on pushes and
  pull requests.

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.
