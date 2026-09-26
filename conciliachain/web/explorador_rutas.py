from .paginas import inicio

RUTAS = {"/": inicio, "/health": lambda: '{"status":"ok"}'}

def resolver(path):
    return RUTAS.get(path, lambda: None)()
