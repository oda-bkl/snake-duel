---
type: gotcha
title: passlib incompatible with bcrypt 5.x
description: passlib's bcrypt handler crashes at import time with bcrypt>=4 due to a removed __about__ attribute and stricter 72-byte enforcement. Use bcrypt directly instead.
tags: [backend, auth, bcrypt, passlib, dependency]
related_files: [backend/store.py, backend/pyproject.toml]
timestamp: 2026-06-23
---

## Symptom

```
AttributeError: module 'bcrypt' has no attribute '__about__'
ValueError: password cannot be longer than 72 bytes
```

Occurs at `CryptContext(schemes=["bcrypt"]).hash(password)` with `bcrypt>=4.0`.

## Root cause

`passlib` has not been updated for bcrypt 4.x, which removed `bcrypt.__about__` and added stricter input validation. The detect-wrap-bug probe passlib runs during backend initialisation triggers the 72-byte error.

## Fix

Remove `passlib` entirely. Use `bcrypt` directly:

```python
import bcrypt

def _hash_pw(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def _check_pw(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())
```

`pyproject.toml` lists `bcrypt>=5.0.0` as a direct dependency; `passlib` is not installed.
