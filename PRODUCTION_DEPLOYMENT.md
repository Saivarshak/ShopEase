# ShopEase production deployment

## Audit summary

ShopEase is a Django 5.2 project rooted at `manage.py`, with the project package in `shopease/` and the commerce app in `store/`. Templates are in `templates/store/`; source static files are in `static/`; collected WhiteNoise assets are written to `staticfiles/`; legacy filesystem uploads use `media/`, while the current upload flow stores images in the `UploadedImage` database table. There are 23 app migrations, Razorpay payment endpoints, Google OAuth support, and a `/health/` endpoint.

No Celery, Redis, Channels, or other background-worker integration was found, so the default Compose stack intentionally contains only Django and PostgreSQL. WhiteNoise serves static files directly, so a separate Nginx container is not required. Add Nginx or Redis only if the application gains a reverse-proxy or worker requirement.

## Media persistence

Render and Railway web-service filesystems are ephemeral: files written under `MEDIA_ROOT` can disappear after a restart, redeploy, or rescheduling. ShopEase's current admin/product upload path writes image bytes to the PostgreSQL `uploaded_images` table (`store.models.UploadedImage`) and serves them through `/assets/...`, so those uploads persist as long as the managed PostgreSQL database is durable and backed up. The legacy `media/uploads/` fallback is **not** durable on a PaaS filesystem. If future code writes files there, configure S3, Cloudinary, or another object store before relying on those uploads. Static files in `static/` are rebuilt by `collectstatic` and are safe to serve through WhiteNoise.

Before this deployment work, the repository had environment-driven settings and the PostgreSQL/WhiteNoise dependencies, but did not have container configuration, a runtime entrypoint, a complete ignore policy, or a discrete PostgreSQL fallback. The checked-in `.env` and SQLite database must be treated as potentially sensitive: rotate any credentials that were ever committed, remove `.env` from Git history where appropriate, and use the untracked `.env` only for local development.

## Files changed

- `shopease/settings.py`: validates production `DEBUG`, requires a production database, supports `DATABASE_URL` and discrete `POSTGRES_*`/`DB_*` variables, configures connection age and optional TLS, and keeps SQLite as a local-only fallback.
- `.env.example`: documents both database formats and production secrets.
- `.gitignore`, `.dockerignore`: exclude credentials, local databases, runtime output, and build artefacts.
- `Dockerfile`: builds a non-root Python image with the production requirements.
- `docker-compose.yml`: starts Django and a health-checked PostgreSQL 16 service with persistent volumes.
- `entrypoint.sh`: runs migrations, collects static files, then starts Gunicorn.
- `Procfile`, `render.yaml`: use the same runtime entrypoint; Render migrations no longer run during the build phase.
- `PRODUCTION_DEPLOYMENT.md`: this audit and operational runbook.

The existing `requirements.txt` and `requirements.production.txt` already include the required `psycopg2-binary`, `dj-database-url`, `whitenoise`, `gunicorn`, and `python-dotenv` packages. No dependency addition was necessary.

## Local PostgreSQL with Docker

1. Copy `.env.example` to `.env` and set a unique `SECRET_KEY`, payment credentials, and a strong `POSTGRES_PASSWORD`. Leave `DATABASE_URL` empty for the Compose setup.
2. Build and start the services:

   ```powershell
   docker compose up --build
   ```

3. In another terminal, create an administrator if needed:

   ```powershell
   docker compose exec web python manage.py createsuperuser
   ```

4. Visit `http://localhost:8000/health/`. Stop the stack with `docker compose down`; add `-v` only when intentionally deleting the local PostgreSQL/media volumes.

## Non-container local commands

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Set DEBUG=true, IS_PRODUCTION=false, and leave DATABASE_URL empty for SQLite.
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py runserver
```

To use PostgreSQL instead, set `DATABASE_URL=postgresql://user:password@localhost:5432/shopease` or set `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, and `POSTGRES_PORT`, then run:

```powershell
python manage.py migrate --noinput
python manage.py collectstatic --noinput
gunicorn shopease.wsgi:application
```

## Render deployment

Create a PostgreSQL database, connect the repository, and use the checked-in `render.yaml` Blueprint. Set `SECRET_KEY`, `DATABASE_URL`, `APP_BASE_URL`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `CORS_ALLOWED_ORIGINS`, and the Razorpay secrets in the Render environment. `DATABASE_SSL_REQUIRE=true` is appropriate for hosted PostgreSQL. The service starts with `sh entrypoint.sh`, which applies migrations before serving traffic.

For any provider, the essential sequence is:

```text
pip install -r requirements.production.txt
python manage.py migrate --noinput
python manage.py collectstatic --noinput
gunicorn --bind 0.0.0.0:$PORT shopease.wsgi:application
```

Keep `DEBUG=false`, use HTTPS, include the deployed hostname in `ALLOWED_HOSTS`, and list complete `https://...` origins in `CSRF_TRUSTED_ORIGINS`. A local filesystem is ephemeral on most PaaS platforms; use the existing database-backed upload flow or object storage for durable media.

## Verification

```powershell
$env:DEBUG='true'; $env:IS_PRODUCTION='false'
python manage.py check
python manage.py test store --verbosity 1
```

For production configuration, run `python manage.py check --deploy` with the production environment loaded. Confirm `/health/`, static assets, login/cart/checkout, admin uploads, payment webhooks, database backups, and HTTPS redirects after release.
