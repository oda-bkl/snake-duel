# ── Stage 1: install frontend deps ───────────────────────────────────────────
FROM oven/bun:1-alpine AS deps
WORKDIR /app
COPY frontend/package.json frontend/bun.lock ./
RUN bun install --frozen-lockfile


# ── Stage 2: build frontend ───────────────────────────────────────────────────
FROM deps AS builder
COPY frontend/ ./
RUN bun run build

# TanStack Start's server bundle exports a fetch() handler (not an HTTP server).
# Call it directly to get the SSR-rendered index.html including the $_TSR
# router manifest that the client bundle requires to hydrate correctly.
RUN printf '%s\n' \
      'import handler from "./server.js";' \
      'const r = await handler.fetch(new Request("http://localhost/"), {}, {});' \
      'if (!r.ok) { process.stderr.write("SSR failed: " + r.status + "\n"); process.exit(1); }' \
      'process.stdout.write(await r.text());' \
    > dist/server/gen.mjs && \
    node dist/server/gen.mjs > dist/client/index.html && \
    echo "SSR index.html: $(wc -c < dist/client/index.html) bytes"


# ── Stage 3: Python backend ───────────────────────────────────────────────────
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev

COPY backend/app ./app
COPY backend/main.py ./
COPY --from=builder /app/dist/client ./frontend

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
