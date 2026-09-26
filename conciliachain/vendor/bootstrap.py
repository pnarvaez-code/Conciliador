"""Bootstrap local sin red ni dependencias opcionales."""
from ..bootstrap import load_ports

def local():
    return load_ports()

bootstrap = local
