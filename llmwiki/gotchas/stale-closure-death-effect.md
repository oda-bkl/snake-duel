---
type: gotcha
title: Stale closure bug in play.tsx death effect; fix using refs
description: The "handle death" useEffect had eslint-disable suppressing a real stale-closure bug where `user` and `running` could be stale when the effect fired.
tags: [react, hooks, stale-closure, play]
related_files: [frontend/src/routes/play.tsx]
timestamp: 2026-06-23
---

**Original code** (buggy):
```tsx
useEffect(() => {
  if (state.alive) return;
  if (running && user && state.score > 0) {   // `running` and `user` could be stale
    api.submitScore(...)
  }
}, [state.alive]); // eslint-disable-line react-hooks/exhaustive-deps
```

`running` and `user` were captured from the closure at the time the effect last registered — not necessarily when `state.alive` became `false`. A user who logged in after the component mounted but before dying could have `user` be `null` in the effect.

**Fix**: mirror mutable values in refs that are always current:
```tsx
const runningRef = useRef(running);
runningRef.current = running;
const userRef = useRef(user);
userRef.current = user;

useEffect(() => {
  if (state.alive) return;
  if (runningRef.current && userRef.current && state.score > 0) {
    api.submitScore(...)
  }
}, [state.alive, state.score, state.mode]);  // no eslint-disable needed
```

`state.score` and `state.mode` are safe in deps because they are part of the same state object that sets `alive: false` — they reflect the death tick values, not later updates.
