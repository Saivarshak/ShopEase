# ShopEase

This project is ready to deploy on Render for a stable production URL.
GitHub Actions in this repository are for CI checks only; deployment should go through Render.

## Recommended hosting

Use Render with the included `render.yaml`. It will create:

- a web service for Django
- a managed PostgreSQL database
- a stable `https://your-service-name.onrender.com` URL
- automatic HTTPS

## Deploy steps

1. Push this project to GitHub.
2. Sign in to Render and create a new Blueprint from this repository.
3. Render will read `render.yaml` and create the `shopease` web service and `shopease-db` database.
4. Enter your `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` when Render prompts for them.
5. After the first deploy finishes, open the Render Shell and run:

```bash
python manage.py createsuperuser
```

6. Your live site will be available at:

```text
https://your-service-name.onrender.com
```

7. If you later connect a custom domain, set these environment variables in Render:

```text
APP_BASE_URL=https://your-domain.com
PAYMENT_CALLBACK_BASE_URL=https://your-domain.com
ALLOWED_HOSTS=your-domain.com,.onrender.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com
```

## Important notes

- Render free services are not recommended for production payments.
- This app now supports `DATABASE_URL` for managed PostgreSQL hosting.
- The sample environment now assumes PostgreSQL when you set explicit DB connection fields outside Render.
- The health check endpoint is available at `/health/`.
- The Dockerfile now respects a platform-provided `PORT`, which helps on hosts like Railway and Render Docker services.
- If you run `python manage.py check --deploy` against the local development `.env`, Django will warn because the local file keeps `DEBUG=True` and uses a development secret key.
- To run a production-style deployment check locally without changing your normal dev settings, use `powershell -ExecutionPolicy Bypass -File .\scripts\check-deploy.ps1`.
