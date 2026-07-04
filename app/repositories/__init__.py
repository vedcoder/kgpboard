"""Data access layer (DAO).

Each module here is the *only* place in the codebase that issues SQL / touches
ORM models for its entity. Higher layers call these functions instead of writing
queries themselves.

Convention:
- Every function takes an `AsyncSession` as its first argument.
- Write functions `flush()` (to emit SQL and surface DB errors) but never
  `commit()` -- the transaction boundary is owned by the caller.
"""
