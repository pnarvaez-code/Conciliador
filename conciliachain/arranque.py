"""Punto de arranque programático y de consola."""
from .bootstrap import load_ports
from .apps.concilia import ejecutar

def iniciar(left=None, right=None):
    if left is None or right is None:
        bank, ledger, _ = load_ports()
        left, right = bank.fetch(), ledger.fetch()
    return ejecutar(left, right)

def main():
    from .cli import main as cli_main
    return cli_main()

if __name__ == "__main__":
    main()
