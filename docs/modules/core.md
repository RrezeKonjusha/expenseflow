# Module: core (shared)

`BaseModel` (abstract entity), permission classes, error format and handler, request-id middleware, JSON logging, MongoDB connection, audit service (`audit.record`), Celery tasks, email adapter with circuit breaker (pybreaker), `/health/`.
Rule (enforced by import-linter): core never imports a business module.
