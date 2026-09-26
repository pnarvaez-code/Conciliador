from html import escape

def pagina(titulo="ConciliaChain", cuerpo=""):
    return "<!doctype html><html lang='es'><head><meta charset='utf-8'>" \
           f"<title>{escape(titulo)}</title><link rel='stylesheet' href='/estilos.css'>" \
           f"</head><body><h1>{escape(titulo)}</h1>{cuerpo}</body></html>"

def inicio():
    return pagina("ConciliaChain", "<p>Conciliación determinista y auditable.</p>")
