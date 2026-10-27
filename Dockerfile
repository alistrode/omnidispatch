FROM node:24.19.0-bookworm-slim AS web
WORKDIR /src/apps/web
COPY apps/web/package*.json ./
RUN npm ci --ignore-scripts
COPY apps/web/ ./
RUN npm run build
FROM python:3.14.0-slim-bookworm
WORKDIR /app
COPY requirements-runtime.lock.txt ./
RUN pip install --no-cache-dir -r requirements-runtime.lock.txt
COPY omnidispatch/ ./omnidispatch/
COPY --from=web /src/omnidispatch/static/ ./omnidispatch/static/
RUN useradd -u 10001 -m omni && mkdir /app/state && chown omni:omni /app/state
USER 10001:10001
EXPOSE 8791
CMD ["python","-m","omnidispatch.cli","--state","/app/state","serve","--host","0.0.0.0"]
