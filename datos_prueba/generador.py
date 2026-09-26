FECHA = "2026-09-01"
FECHA_BANCO = "2026-09-02"
FECHA_TRANSFERENCIA = "2026-09-03"

def empresa():
    filas = []
    for k in range(40):
        filas.append({"fecha": FECHA, "monto": 151000 + k * 71000,
                      "referencia": f"FV-{4001+k:04d}", "descripcion": "VENTA TARJETA"})
    for monto in (85000,210000,335000,460000,585000,710000,835000,960000,1085000,1210000):
        filas.append({"fecha": FECHA, "monto": monto, "referencia": "", "descripcion": "VENTA EFECTIVO"})
    for monto in (1200000,1500000,1800000,2100000,2400000):
        filas.append({"fecha": FECHA, "monto": monto, "referencia": "", "descripcion": "VENTA POR TRANSFERENCIA BANCARIA"})
    for monto in (555555,666666,777777,888888,999999):
        filas.append({"fecha": FECHA, "monto": monto, "referencia": "", "descripcion": "VENTA LOCAL"})
    return filas

def banco():
    filas = []
    for k in range(40):
        filas.append({"fecha": FECHA, "monto": 151000 + k * 71000,
                      "referencia": f"FV-{4001+k:04d}", "descripcion": "COBRO TARJETA"})
    for monto in (85000,210000,335000,460000,585000,710000,835000,960000,1085000,1210000):
        filas.append({"fecha": FECHA_BANCO, "monto": monto, "referencia": "", "descripcion": "DEPOSITO EFECTIVO"})
    for monto in (1200000,1500000,1800000,2100000,2400000):
        filas.append({"fecha": FECHA_TRANSFERENCIA, "monto": round(monto*.98),
                      "referencia": "", "descripcion": "ABONO POR TRANSFERENCIA"})
    for monto in (123456,754321,1111111):
        filas.append({"fecha": FECHA_BANCO, "monto": monto, "referencia": "", "descripcion": "DEPOSITO NO IDENTIFICADO"})
    return filas

def generar_registros():
    return empresa(), banco()

def generar():
    return generar_registros()

def ejemplos():
    e, b = generar_registros()
    return {"empresa": e[:8], "banco": b[:8], "csv_tocado_excel": [{"fecha": "45236", "monto": "151.000"}] + e[1:8]}

def escribir_ejemplos(directorio="ejemplos"):
    import csv, json
    from pathlib import Path
    destino = Path(directorio); destino.mkdir(parents=True, exist_ok=True)
    datos = ejemplos()
    for nombre, filas in (("empresa_8.csv", datos["empresa"]), ("banco_8.csv", datos["banco"]),
                          ("empresa_8.xml", datos["empresa"])):
        ruta = destino / nombre
        if ruta.suffix == ".csv":
            campos = sorted({clave for fila in filas for clave in fila})
            with ruta.open("w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=campos); w.writeheader(); w.writerows(filas)
        else:
            from utilidades.exportar import a_xml
            ruta.write_text(a_xml(filas), encoding="utf-8")
    tocado = destino / "empresa_tocado_excel.csv"
    filas = list(datos["csv_tocado_excel"])
    with tocado.open("w", newline="", encoding="utf-8") as f:
        campos = sorted({clave for fila in filas for clave in fila})
        w = csv.DictWriter(f, fieldnames=campos); w.writeheader(); w.writerows(filas)
    (destino / "datos.json").write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
    return destino
