# ConciliaChain

ConciliaChain es una aplicación de conciliación financiera determinista,
auditable y completamente disponible en español. Permite cargar movimientos de
una empresa y de un banco, cerrar lotes, emitir extractos, verificar su
integridad criptográfica y encontrar coincidencias en varios niveles de
confianza.

El repositorio ofrece dos formas de uso:

1. **Aplicación Python local**, con SQLite, servidores HTTP y procesos separados
   para empresa, banco, conciliación y visor.
2. **Aplicación web estática**, publicable en GitHub Pages y utilizable sin
   instalar Python. Esta versión conserva la memoria en el navegador.

> El núcleo no utiliza dependencias de terceros. Está pensado para Python 3.10
> o superior y usa únicamente módulos de la biblioteca estándar.

## Funcionalidades

- Registro de movimientos de empresa y banco.
- Persistencia local con SQLite.
- Cierre de lotes y emisión de extractos CSV, XML y JSON.
- Cadena JSONL append-only con huellas SHA-256.
- Huella de cada movimiento, archivo, raíz de lote y bloque anterior.
- Propagación de bloques entre copias y detección de brechas.
- Verificación de cadenas, archivos y movimientos.
- Conciliación en tres niveles:
  - **Nivel 1:** referencia coincidente sin distinguir mayúsculas y monto
    exacto.
  - **Nivel 2:** monto exacto y fecha con una diferencia máxima de tres días.
  - **Nivel 3:** palabras comunes en la descripción y diferencia de monto de
    hasta el cinco por ciento.
- Uso de cada movimiento bancario como máximo una vez.
- Explicaciones para movimientos pendientes.
- Registro JSONL de eventos de reinicio, registro, emisión, verificación,
  alertas, conciliación e informes.
- Datos de prueba deterministas: 60 movimientos de empresa, 58 del banco y
  55 cruces esperados.
- Aplicaciones web independientes en los puertos 5000 a 5003.
- Modo unificado en el puerto 8080.
- Interfaz estática para GitHub Pages con memoria persistente del navegador.

## Requisitos

- Python 3.10 o superior para la aplicación local.
- Navegador moderno para la versión web.
- Node.js es opcional y solo se utiliza para comprobar la sintaxis de
  `docs/app.js`.

No es necesario ejecutar `pip install`: `requirements.txt` documenta que el
núcleo usa exclusivamente la biblioteca estándar.

## Estructura del proyecto

```text
.
├── arranque.py                 # Inicialización y arranque multiproceso
├── config.py                   # Puertos, rutas, colores y configuración
├── modelo.py                   # SQLite y tabla movimientos
├── servidor.py                 # Servidor HTTP de las aplicaciones
├── nucleo/
│   ├── sello.py                # Huellas, bloques y verificación
│   ├── conciliar.py            # Algoritmo de conciliación
│   ├── eventos.py              # Eventos JSONL
│   └── llamadas.py             # Llamadas HTTP estándar
├── apps/                       # Empresa, banco, concilia, visor y unificado
├── utilidades/
│   ├── emision.py              # Emisión y sellado de lotes
│   └── exportar.py             # Exportación CSV, XML y JSON
├── datos_prueba/generador.py   # Dataset determinista y ejemplos
├── web/                        # Helpers de presentación Python
├── docs/                       # Aplicación estática para GitHub Pages
├── tests/                      # Pruebas unitarias y end-to-end
└── .github/workflows/pages.yml # Publicación automática de docs/
```

## Instalación y ejecución local

Clona el repositorio y entra en su directorio:

```powershell
git clone https://github.com/pnarvaez-code/Conciliador.git
cd Conciliador
```

### Flujo completo con cuatro aplicaciones

`arranque.py` limpia y prepara los datos de prueba, genera el lote inicial,
emite extractos, registra el reinicio y levanta los cuatro procesos:

```powershell
python arranque.py
```

La aplicación de conciliación queda disponible en
`http://127.0.0.1:5000`, empresa en `5001`, banco en `5002` y visor en `5003`.
Presiona `Ctrl+C` para detener los procesos.

### Modo unificado

Para ejecutar una sola aplicación en el puerto 8080:

```powershell
$env:CC_MODO = "unificado"
python arranque.py
```

También puede iniciarse directamente:

```powershell
python apps/unificado.py
```

En Linux o macOS:

```bash
CC_MODO=unificado python arranque.py
```

### CLI

```powershell
python -m conciliachain.cli reconcile --json
python -m conciliachain.cli serve --port 8080
```

La primera orden ejecuta una conciliación determinista y devuelve JSON. La
segunda inicia un servidor HTTP unificado compatible con el núcleo existente.

## API HTTP

Las aplicaciones aceptan y devuelven JSON salvo las rutas de descarga.

### Empresa (`5001`)

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/` | Estado y cantidad de movimientos |
| GET | `/cadena` | Bloques y resultado de verificación |
| POST | `/registrar` | Registra un movimiento |
| POST | `/cerrar_lote` | Sella un lote |
| POST | `/emitir_extracto?formato=csv` | Emite CSV |
| POST | `/emitir_extracto?formato=xml` | Emite XML |
| POST | `/verificar/<lote>` | Verifica cadena y archivo del lote |
| GET | `/descargar_csv` | Descarga los movimientos como CSV |

El banco (`5002`) ofrece las mismas operaciones aplicadas a sus movimientos.

Ejemplo de registro:

```powershell
curl.exe -X POST http://127.0.0.1:5001/registrar `
  -H "Content-Type: application/json" `
  -d '{"fecha":"2026-09-01","monto":151000,"referencia":"FV-4001","descripcion":"VENTA TARJETA"}'
```

Ejemplo de cierre, emisión y verificación:

```powershell
curl.exe -X POST http://127.0.0.1:5001/cerrar_lote `
  -H "Content-Type: application/json" `
  -d '{"lote":"LOTE-20260901"}'

curl.exe -X POST "http://127.0.0.1:5001/emitir_extracto?formato=csv" `
  -H "Content-Type: application/json" `
  -d '{"lote":"LOTE-20260901"}'

curl.exe -X POST http://127.0.0.1:5001/verificar/LOTE-20260901
```

### Conciliación (`5000`)

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/` | Estado del servicio |
| GET | `/resultado` | Último resultado calculado |
| POST | `/conciliar` | Ejecuta la conciliación |
| POST | `/verificar/<lote>` | Verifica un lote |
| GET | `/descargar_csv` | Descarga datos conciliables |
| GET | `/eventos` | Consulta eventos registrados |

El visor (`5003`) es de solo lectura. El modo unificado (`8080`) combina la
superficie principal en un único proceso.

## Modelo de datos

La tabla SQLite `movimientos` contiene:

```text
id           INTEGER PRIMARY KEY
lote         TEXT
fecha        TEXT
monto        INTEGER
referencia   TEXT
descripcion  TEXT
```

Las bases se crean debajo de `datos/<actor>/`. El archivo de eventos general
queda en `datos/eventos.jsonl`. Estos archivos son datos runtime locales y no
deben versionarse.

## Integridad y sellado

Cada movimiento se normaliza como:

```text
fecha|int(monto)|REFERENCIA EN MAYÚSCULAS|descripción recortada
```

La cadena comienza con `GENESIS`, definido como 64 ceros. Cada bloque registra
el índice, origen, lote, nombre del archivo, número de movimientos, huellas de
movimientos, raíz, huella del archivo, huella anterior, timestamp y huella del
bloque. Si un byte del archivo o un campo de la cadena cambia, la verificación
falla y se genera una alerta de brecha.

Las funciones principales están disponibles en `nucleo/sello.py`:

```python
from nucleo.sello import (
    crear_bloque,
    huella_movimiento,
    verificar_archivo,
    verificar_cadena,
)
```

## Datos de prueba

El generador usa fechas fijas para que los resultados sean reproducibles:

```text
Empresa:       2026-09-01
Banco:         2026-09-02
Transferencias: 2026-09-03
```

Para crear ejemplos CSV, XML y el archivo CSV modificado por Excel:

```powershell
python -c "from datos_prueba.generador import escribir_ejemplos; escribir_ejemplos()"
```

Los archivos se crean en `ejemplos/`. El dataset contiene tarjetas, efectivo,
transferencias, ventas locales pendientes, depósitos no identificados y
variaciones de monto para ejercitar los tres niveles de conciliación.

## Aplicación web para GitHub Pages

La carpeta `docs/` contiene una SPA sin backend. El workflow
`.github/workflows/pages.yml` la publica automáticamente en cada push a
`main`, siempre que GitHub Pages esté configurado con la fuente **GitHub
Actions**.

La aplicación web permite:

- registrar movimientos de empresa y banco;
- ejecutar la conciliación desde el navegador;
- visualizar cruces por nivel y pendientes;
- cerrar lotes y guardar su huella;
- consultar el historial de eventos;
- exportar toda la memoria como JSON;
- importar una memoria previamente exportada;
- borrar los datos locales del navegador.

La memoria se guarda en IndexedDB y mantiene un respaldo en localStorage. Es
intencionalmente local: GitHub Pages sirve archivos estáticos y no ofrece una
base de datos compartida. Para mover datos entre equipos, utiliza **Exportar
memoria** e **Importar memoria**. Para una memoria central multiusuario se
necesitaría añadir una API autenticada y un almacenamiento remoto.

## Pruebas y validaciones

Ejecuta la compilación y todas las pruebas:

```powershell
python -m compileall -q .
python -m unittest discover -v
```

La suite cubre:

- conciliación determinista;
- persistencia SQLite;
- cierre y emisión de lotes;
- exportación de ejemplos;
- verificación de integridad;
- detección de alteración de un archivo;
- cuatro rutas HTTP principales;
- generación de 55 cruces a partir de 60/58 movimientos.

Para validar la sintaxis JavaScript de la versión web, si Node.js está
disponible:

```powershell
node --check docs/app.js
```

## Configuración

Las variables opcionales son:

| Variable | Valor predeterminado | Uso |
|---|---:|---|
| `CC_MODO` | `separado` | Usa `unificado` para el servidor 8080 |
| `PORT` | `8080` | Puerto del modo unificado |
| `CC_DATOS` | `datos` | Directorio de bases, cadenas y eventos |

Los puertos separados son fijos por contrato: concilia `5000`, empresa `5001`,
banco `5002` y visor `5003`.

## Limitaciones y seguridad

- La aplicación local está orientada a demostraciones, integración y flujos
  controlados; no reemplaza un sistema contable regulado.
- La memoria de GitHub Pages es local al navegador y no tiene autenticación ni
  sincronización multiusuario.
- Los archivos de datos pueden contener información financiera sensible.
  Mantén `datos/`, exportaciones JSON y extractos fuera de repositorios
  públicos.
- La cadena garantiza detección de modificaciones posteriores, pero no
  sustituye controles de acceso, gestión de claves ni una firma digital
  externa.

## Licencia y contribuciones

Antes de abrir cambios, ejecuta la suite de pruebas y conserva el uso de la
biblioteca estándar en el núcleo. Las nuevas rutas o cambios en el formato de
eventos deben documentarse en este README y acompañarse de una prueba
end-to-end.
