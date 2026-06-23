---
type: gotcha
title: SSR hydration mismatch from useTheme reading localStorage on first render
description: Reading localStorage/matchMedia in useState initializer causes server/client mismatch because SSR always returns "dark" but the browser may return "light".
tags: [ssr, hydration, theme, react]
related_files: [frontend/src/hooks/useTheme.ts, frontend/src/routes/__root.tsx]
timestamp: 2026-06-23
---

## Symptom

React throws `Hydration failed because the server rendered HTML didn't match the client` pointing at the Moon/Sun icon in `AppHeader`. The server renders one icon, the client renders the other.

## Root cause

`useTheme` called `getInitialTheme()` as the `useState` initializer. That function reads `localStorage` and `matchMedia` in the browser, but returns `"dark"` during SSR (`typeof window === "undefined"`). If the user's stored preference is `"light"`, the first client render disagrees with SSR HTML.

## Fix

Always initialize state to `"dark"` (matching the SSR default) and read the real preference in a `useEffect` that runs only on the client after hydration. Combine with `suppressHydrationWarning` on `<body>` to silence browser-extension attribute noise (e.g. `cz-shortcut-listen`).
