## Project Outline
Interactive Snake game
- two modes (walls and pass-through)
- multi-user (leaderboard, watch active games, login and signup)

## Backend
use uv for dependency management. a few useful commands:
```
uv sync
uv add <package>
uv run python
```

## General notes
- regularly commit code to git
- the frontend code was written by an external freelancer i don't necessarily trust. 
- Use red-green-refactor for all business logic and API endpoints. Write the failing test first, then the implementation. Exemptions: database migrations, config files, scripts.
- At the **start** of each working session, read `llmwiki/index.md` and any entries relevant to today's task before writing any code.
- At the **end** of each working session, review what was built and update the wiki before closing. Prompt: "Update the wiki with anything learned this session."

## LLM Wiki (Open Knowledge Format)

Maintain a living knowledge base in `llmwiki/` as you work. This is an OKF bundle:
each concept is one markdown file with YAML frontmatter.

### When to write to the wiki
- After implementing a non-obvious architectural decision → `llmwiki/decisions/`
- After discovering how two systems integrate → `llmwiki/integrations/`
- After debugging a tricky issue and finding the root cause → `llmwiki/gotchas/`
- After stabilizing an API contract → `llmwiki/apis/`
- After understanding a data schema → `llmwiki/schemas/`

### File format (required)
Every file must start with:
```yaml
---
type: 
title: 
description: 
tags: [relevant, tags]
related_files: [<relative/path/to/file>, <relative/path/to/other_file>]
timestamp: 
---
```

### Rules
- Write entries *after* the work is done, not speculatively
- Cross-link related entries using relative markdown links
- Update `llmwiki/index.md` when adding a new category
- Prefer updating an existing entry over creating a duplicate
- Entries are written for future LLM agents, not humans — be precise,
  include exact identifiers, file paths, and error messages