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

## Versión web para GitHub Pages

La carpeta `docs/` contiene una aplicación estática en español. Se publica
automáticamente mediante `.github/workflows/pages.yml` y no necesita servidor
Python: la memoria se conserva en IndexedDB del navegador, con respaldo en
`localStorage`. La interfaz permite registrar movimientos de empresa y banco,
cerrar lotes, ejecutar conciliaciones, consultar eventos y exportar/importar
una copia JSON de la memoria. El botón **Borrar memoria** elimina únicamente
los datos del navegador actual.

En el repositorio, activa GitHub Pages con la fuente **GitHub Actions**. La
aplicación es deliberadamente local: GitHub Pages no puede guardar datos en un
servidor compartido sin añadir una API externa. Para compartir el estado,
usa **Exportar memoria** e importa el archivo en otro navegador.
