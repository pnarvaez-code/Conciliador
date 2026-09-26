# ConciliaChain

Proyecto Python 3.10+ para conciliación determinista y auditable. El núcleo usa
exclusivamente la biblioteca estándar: SQLite, JSONL encadenado (SHA-256),
propagación/verificación, eventos y conciliación de tres niveles (referencia,
clave contable/fecha/importe, e importe dentro de tolerancia).

```powershell
python -m conciliachain.cli reconcile --json
python -m conciliachain.cli serve --port 8080
```

Rutas: `GET /health`, `GET /api/reconcile` y `POST /api/reconcile` con
`{"left": [...], "right": [...]}`. Los puertos `BankPort`, `LedgerPort`,
`ImportPort` y `UnifiedPort` están en `conciliachain.apps`; bootstrap local
usa fallback determinista si no hay configuración externa.
