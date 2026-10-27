# syntax=docker/dockerfile:1
FROM node:24.19.0-bookworm-slim AS web
WORKDIR /src/apps/web
COPY apps/web/package*.json ./
RUN --mount=type=secret,id=proxy_ca <<'SH'
set -eu
if [ -f /run/secrets/proxy_ca ]; then export NODE_EXTRA_CA_CERTS=/run/secrets/proxy_ca; fi
npm ci --ignore-scripts --strict-ssl=true
SH
COPY apps/web/ ./
RUN npm run build
FROM python:3.14.10-slim-bookworm
WORKDIR /app
COPY requirements-runtime.lock.txt ./
RUN --mount=type=secret,id=system_ca <<'SH'
set -eu
if [ -f /run/secrets/system_ca ]; then export PIP_CERT=/run/secrets/system_ca; fi
pip install --no-cache-dir -r requirements-runtime.lock.txt
SH
COPY omnidispatch/ ./omnidispatch/
COPY --from=web /src/omnidispatch/static/ ./omnidispatch/static/
RUN useradd -u 10001 -m omni && mkdir /app/state && chown omni:omni /app/state && chmod -R a+rX /app/omnidispatch
USER 10001:10001
EXPOSE 8791
CMD ["python","-m","omnidispatch.cli","--state","/app/state","serve","--host","0.0.0.0"]
