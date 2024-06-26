FROM python:3.12.2-slim-bookworm AS python_base

ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install -y --no-install-recommends \
      build-essential gdb lcov pkg-config \
      libbz2-dev libffi-dev libgdbm-dev libgdbm-compat-dev liblzma-dev \
      libncurses5-dev libreadline6-dev libsqlite3-dev libssl-dev \
      lzma lzma-dev tk-dev uuid-dev zlib1g-dev libmariadb-dev
COPY requirements-prod.txt /requirements-prod.txt
RUN pip install --no-cache-dir -r /requirements-prod.txt
RUN rm /requirements-prod.txt

FROM python_base AS builder
ENV DJANGO_SETTINGS_MODULE=devicemanager.settings_prod
ENV DEBUG 0
WORKDIR /app
COPY . /app
RUN mkdir -p /app/build/static /app/build/media
RUN ["./manage.py", "collectstatic", "--noinput"]

FROM nginx:1.26 AS static-server
ENV DEBUG 0
COPY --from=builder --chown=nginx:nginx /app/build/static /usr/share/nginx/static
COPY --from=builder --chown=nginx:nginx /app/build/media /usr/share/nginx/media
COPY ./docker/static.nginx.conf /etc/nginx/conf.d/default.conf

FROM python_base AS application-server
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0
ENV DJANGO_SETTINGS_MODULE=devicemanager.settings_prod
RUN addgroup --system --gid 1001 device-manager
RUN adduser --system --uid 1001 device-manager
USER device-manager
WORKDIR /home/device-manager/app
VOLUME ./media
COPY --from=builder --chown=device-manager:device-manager /app .
CMD ["gunicorn", "--workers=4", "-b 0.0.0.0:8000", "--capture-output", "--log-level=info", "--access-logfile=-", "--error-logfile=-", "devicemanager.wsgi"]
