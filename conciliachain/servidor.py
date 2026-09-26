"""Alias estable para arrancar el servidor HTTP."""
from .http import handler_factory, serve
__all__ = ["handler_factory", "serve"]

if __name__ == "__main__":
    serve()
