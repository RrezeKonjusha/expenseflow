# Module: accounts (Authentication)

**Public API:** `/api/v1/auth/` register, activate, login, refresh, logout, me, password/change, password/forgot, password/reset (see Swagger tag *Auth*).
**Layers:** `api/views.py` (cookies, throttles) -> `services.py` (use cases) -> `users.models.User`; tokens in `tokens.py`.
**Design decisions:** access token in memory (15 min); refresh token rotated and blacklisted, sent only as an httpOnly SameSite=Strict cookie scoped to `/api/v1/auth/`; activation and reset links are signed, stateless and single-use.
**Logging and monitoring:** audit events `USER_REGISTERED`, `USER_ACTIVATED`, `LOGIN`, `LOGOUT`, `PASSWORD_*`; failed logins tracked by django-axes; logs under `apps.accounts`.
**Tests:** `apps/accounts/tests/`.
