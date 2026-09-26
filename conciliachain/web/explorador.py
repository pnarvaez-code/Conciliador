from .paginas import pagina

def explorar(results):
    rows = []
    for result in results:
        item = result.to_dict() if hasattr(result, "to_dict") else result
        rows.append("<tr>" + "".join(f"<td>{item.get(k, '')}</td>"
                    for k in ("left_id", "right_id", "status", "level", "difference")) + "</tr>")
    return pagina("Resultados", "<table><tr><th>Origen</th><th>Destino</th><th>Estado</th>"
                  "<th>Nivel</th><th>Diferencia</th></tr>" + "".join(rows) + "</table>")
