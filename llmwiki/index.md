# LLM Wiki — Snake Arena

## Categories

- [decisions/](decisions/) — non-obvious architectural choices
- [integrations/](integrations/) — how systems connect
- [schemas/](schemas/) — data shapes and field semantics
- [apis/](apis/) — stabilised API contracts
- [gotchas/](gotchas/) — tricky bugs and their root causes

## Entries

- [decisions/api-service-interface.md](decisions/api-service-interface.md) — Why ApiService is an interface with mock and real implementations
- [decisions/theme-system.md](decisions/theme-system.md) — Light/dark theme via CSS custom properties and .dark class
- [decisions/active-game-id-ownership.md](decisions/active-game-id-ownership.md) — Server owns game IDs; id is optional in upsertActiveGame
- [decisions/subscribe-pattern.md](decisions/subscribe-pattern.md) — Callback-based subscribe* methods; polling in realApi, SSE/WS future
- [decisions/backend-module-structure.md](decisions/backend-module-structure.md) — FastAPI split into models/store/auth/routers; singleton store pattern for tests
- [decisions/in-memory-store.md](decisions/in-memory-store.md) — In-memory Store dataclass, bcrypt auth, seed data, migration path
- [integrations/auth-token-flow.md](integrations/auth-token-flow.md) — How the auth token flows from login to HTTP requests
- [schemas/frontend-types.md](schemas/frontend-types.md) — Core TypeScript types: User, AuthSession, ScoreEntry, ActiveGame
- [apis/backend-rest-api.md](apis/backend-rest-api.md) — Full REST API contract; canonical source is openapi.yaml
- [gotchas/stale-closure-death-effect.md](gotchas/stale-closure-death-effect.md) — Stale closure bug in play.tsx death effect; fix using refs
- [gotchas/passlib-bcrypt-compat.md](gotchas/passlib-bcrypt-compat.md) — passlib crashes with bcrypt>=4; use bcrypt directly instead
- [gotchas/bun-not-installed.md](gotchas/bun-not-installed.md) — Codespace has npm not bun; all frontend Makefile targets use npm
