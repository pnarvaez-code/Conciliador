from datetime import date
def explicar_pendiente(a, bancos):
    if not bancos: return "sin candidato"
    for b in bancos:
        if a["fecha"] == b["fecha"] and a["monto"] != b["monto"]: return "mismo día monto distinto"
        if a.get("descripcion","").split() and abs(a["monto"]-b["monto"]) > a["monto"]*.05: return "descripción parecida monto demasiado diferente"
    return "fecha lejana"
def conciliar(empresa, banco):
    usados=set(); pares=[]; pendientes=[]
    for a in empresa:
        elegido=None; nivel=0
        for i,b in enumerate(banco):
            if i in usados: continue
            if a.get("referencia","").strip().upper() and a.get("referencia","").strip().upper()==b.get("referencia","").strip().upper() and a["monto"]==b["monto"]: elegido,nivel=i,1; break
        if elegido is None:
            for i,b in enumerate(banco):
                if i not in usados and a["monto"]==b["monto"] and abs(int(a["fecha"][8:])-int(b["fecha"][8:]))<=3: elegido,nivel=i,2; break
        if elegido is None:
            for i,b in enumerate(banco):
                comunes=set(a.get("descripcion","").upper().split()) & set(b.get("descripcion","").upper().split())
                if i not in usados and comunes and abs(a["monto"]-b["monto"])<=a["monto"]*.05: elegido,nivel=i,3; break
        if elegido is None: pendientes.append({"empresa":a,"explicacion":explicar_pendiente(a,banco)})
        else: usados.add(elegido); pares.append({"empresa":a,"banco":banco[elegido],"nivel":nivel})
    pendientes += [{"banco": b, "explicacion":"sin candidato"} for i,b in enumerate(banco) if i not in usados]
    return pares, pendientes
