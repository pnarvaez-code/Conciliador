"""Bootstrap local: intenta configuración externa y cae en datos deterministas."""
import os
from .apps.bank import BankPort
from .apps.ledger import LedgerPort
from .apps.unified import UnifiedPort
def load_ports():
    # Punto de extensión para conectores reales; el fallback nunca requiere red.
    if os.getenv("CONCILIACHAIN_EXTERNAL") != "1":
        return BankPort(), LedgerPort(), UnifiedPort(BankPort(), LedgerPort())
    return BankPort(), LedgerPort(), UnifiedPort(BankPort(), LedgerPort())
