"""ConciliaChain: núcleo de conciliación auditable, sin dependencias externas."""
from .models import Record, ReconciliationResult
from .reconciliation import reconcile

__all__ = ["Record", "ReconciliationResult", "reconcile"]
__version__ = "0.1.0"
