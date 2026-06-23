---
type: decision
title: Light/dark theme via CSS custom properties and .dark class
description: :root defines light theme; .dark overrides to dark. useTheme hook toggles the class on <html> and persists to localStorage.
tags: [css, theme, tailwind]
related_files: [frontend/src/styles.css, frontend/src/hooks/useTheme.ts, frontend/src/components/AppHeader.tsx]
timestamp: 2026-06-23
---

Tailwind 4 is configured with `@custom-variant dark (&:is(.dark *))` — dark mode activates when any ancestor has class `dark`.

`:root` = light theme (light blue-gray backgrounds, darker teal primary `oklch(0.62 0.18 175)`).
`.dark` = dark gaming theme (near-black backgrounds, bright teal primary `oklch(0.78 0.17 175)`).

`useTheme` (`src/hooks/useTheme.ts`):
- Reads initial preference from `localStorage` key `snake.theme`, falling back to `prefers-color-scheme`.
- Adds/removes `dark` class on `document.documentElement`.
- Exports `{ theme, toggle }`.

The toggle button (sun/moon icon) lives in `AppHeader`. The original codebase had `:root` set to dark values with no light theme — this was a bug from the freelancer.

Game board colors are separate CSS custom properties (`--game-board`, `--game-snake`, etc.) defined in both `:root` and `.dark` because the canvas reads them via `getComputedStyle`.
