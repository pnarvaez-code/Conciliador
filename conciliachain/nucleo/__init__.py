"""Fachada del núcleo (se mantienen alias para integraciones existentes)."""
from ..models import Record, ReconciliationResult
from ..reconciliation import reconcile, conciliar
from ..seal import GENESIS

__all__ = ["Record", "ReconciliationResult", "reconcile", "conciliar", "GENESIS"]
