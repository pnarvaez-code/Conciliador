import json
from urllib.request import Request, urlopen
def llamar(url, metodo="GET", datos=None):
    cuerpo=None if datos is None else json.dumps(datos).encode()
    req=Request(url,data=cuerpo,method=metodo,headers={"Content-Type":"application/json"})
    with urlopen(req) as r: return json.loads(r.read().decode())
