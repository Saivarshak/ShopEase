FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN addgroup --system django && adduser --system --ingroup django django

COPY requirements.production.txt requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.production.txt

COPY . .
RUN mkdir -p /app/media /app/staticfiles && chown -R django:django /app

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER django
EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
