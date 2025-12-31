

**Celery **

1. **Separate Celery workers** - each app needs its own worker
2. **Different Redis DBs** - Superset uses `redis:6379/0`, StatementParser uses `redis:6379/1` (isolation)
3. **Different queues** - `-Q superset` vs `-Q statement_parser`
4. **Fixed indentation** - your original had inconsistent indentation
5. **Shared resources** - Redis and Postgres are shared via `shared_network`
6. **Exposed Redis port** - so both apps can access it

**Architecture:**
```
┌─────────────────────────────────────────────────────────┐
│                    Shared Redis                         │
│                  (DB 0: Superset)                       │
│                  (DB 1: StatementParser)                │
└─────────────────────────────────────────────────────────┘
        │                                   │
        ▼                                   ▼
┌───────────────────┐             ┌───────────────────┐
│ Superset Worker   │             │ Parser Worker     │
│ Queue: superset   │             │ Queue: statement  │
└───────────────────┘             └───────────────────┘
