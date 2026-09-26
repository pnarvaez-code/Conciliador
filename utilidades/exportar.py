import csv, io, json, xml.etree.ElementTree as ET

def _fila(x):
    return dict(x) if isinstance(x, dict) else x.to_dict()

def a_json(items, indent=None):
    return json.dumps([_fila(x) for x in items], ensure_ascii=False, indent=indent, default=str)

def a_csv(items):
    filas = [_fila(x) for x in items]
    if not filas: return ""
    salida = io.StringIO()
    campos = list(filas[0])
    w = csv.DictWriter(salida, fieldnames=campos, extrasaction="ignore")
    w.writeheader(); w.writerows(filas)
    return salida.getvalue()

def a_xml(items, raiz="extracto"):
    root = ET.Element(raiz)
    for fila in items:
        nodo = ET.SubElement(root, "movimiento")
        for clave, valor in _fila(fila).items():
            ET.SubElement(nodo, str(clave)).text = str(valor)
    return ET.tostring(root, encoding="unicode")

exportar_csv = a_csv
exportar_json = a_json
exportar_xml = a_xml
