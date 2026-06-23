---
type: gotcha
title: Relative /api paths hit the frontend server in GitHub Codespaces
description: In Codespaces each port gets its own hostname, so relative /api/* fetches go to the Vite server (8080) not FastAPI (8000). Fix: Vite dev proxy.
tags: [codespaces, proxy, vite, networking]
related_files: [frontend/vite.config.ts, frontend/src/services/httpClient.ts]
timestamp: 2026-06-23
---

## Symptom

`POST /api/auth/signup` returns 404. The request URL shows the frontend's Codespaces hostname on port 8080, not port 8000.

## Root cause

GitHub Codespaces gives each forwarded port its own unique HTTPS hostname (e.g. `...-8080.app.github.dev`). Relative paths like `/api/auth/signup` resolve to the frontend host, not the backend. Unlike localhost dev, there's no shared origin.

## Fix

Add a Vite dev server proxy in `vite.config.ts`:

```ts
vite: {
  server: {
    proxy: { "/api": "http://localhost:8000" },
  },
}
```

The Vite dev server then forwards all `/api/*` requests to FastAPI internally (on localhost, where port routing works normally). `httpClient.ts` uses `VITE_API_URL ?? ""` so no env var change is needed for local dev.
