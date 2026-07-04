"""Service (business logic) layer.

Services orchestrate repositories, enforce business rules, own the transaction
boundary (commit/rollback), and raise domain errors from
`app.core.exceptions`. They know nothing about HTTP.
"""
