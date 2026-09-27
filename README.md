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
- Blockchain local append-only con bloque génesis, `previous_hash`, nonce y
  prueba de trabajo.
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

La blockchain de ConciliaChain es un libro mayor local orientado a la
trazabilidad de lotes y eventos. No es una criptomoneda ni depende de una red
pública: cada bloque contiene transacciones de gestión, el hash del bloque
anterior, un nonce y un hash SHA-256 que debe cumplir la dificultad configurada.
La cadena se valida completa antes de presentarse como íntegra. El módulo
`nucleo/blockchain.py` contiene la implementación Python y la SPA mantiene una
réplica equivalente en el navegador.

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
│   ├── blockchain.py           # Blockchain, minería y validación
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

### Inicio sencillo en Windows

Si descargaste el repositorio como ZIP, no necesitas escribir comandos:

1. Instala Python 3.10 o superior desde
   [python.org](https://www.python.org/downloads/windows/). Durante la
   instalación activa **Add Python to PATH**.
2. Abre la carpeta del proyecto.
3. Haz doble clic en `ejecutar_web.bat`.
4. El navegador abrirá la aplicación web con memoria y blockchain local en
   `http://127.0.0.1:8000`.

Para arrancar también los servicios Python de empresa, banco, conciliación y
visor, haz doble clic en `ejecutar.bat`. La ventana negra debe permanecer
abierta mientras uses los servicios; presiona `Ctrl+C` para detenerlos.

`ejecutar_web.bat` solo necesita Python para servir los archivos estáticos. Si
Python no está instalado, abre `docs/index.html` directamente, aunque algunos
navegadores pueden restringir el almacenamiento local al usar archivos `file://`.

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

### Flujo recomendado de trabajo

Para una operación diaria, utiliza este orden:

1. Inicia la aplicación y comprueba `GET /health` en los servicios que vayas a
   utilizar.
2. Registra cada movimiento con el actor correcto (`empresa` o `banco`).
3. Cierra el lote cuando el origen haya terminado de cargar movimientos.
4. Emite el extracto en el formato que necesite el sistema receptor.
5. Verifica el lote antes de compartir el archivo.
6. Ejecuta la conciliación desde `5000` o desde el modo unificado.
7. Revisa los pendientes y conserva el resultado junto con el evento de
   conciliación.

El cierre de lote es el punto de control: después de cerrar un lote, cualquier
modificación del archivo asociado debe provocar una verificación inválida.
Para corregir datos, genera un nuevo lote; no edites manualmente una cadena
existente.

### Blockchain y prueba de trabajo

Además de la cadena de sellos de archivos, `Blockchain` mantiene un libro mayor
de bloques:

```python
from nucleo.blockchain import Blockchain

cadena = Blockchain(dificultad=2)
cadena.agregar([
    {"tipo": "lote_emitido", "lote": "LOTE-001", "cantidad": 60}
])
assert cadena.validar()
```

El bloque génesis usa `hash_anterior` compuesto por 64 ceros. Los siguientes
bloques enlazan exactamente con `hash_bloque` del anterior. Para minar, el
nonce se incrementa hasta que el hash empiece con la cantidad de ceros indicada
por `dificultad`. Si se cambia una transacción, el timestamp, el nonce o
cualquier enlace, `validar()` devuelve `False`.

La aplicación web crea un bloque para cada movimiento registrado, cada lote
cerrado y cada conciliación ejecutada. La pestaña **Blockchain** muestra el
génesis, el índice, el nonce, el hash actual, el hash anterior, la cantidad de
transacciones y el estado de integridad. La dificultad web es deliberadamente
baja para que el navegador siga siendo usable; la blockchain local no pretende
ofrecer seguridad económica frente a un atacante con control del navegador.

## API HTTP

Las aplicaciones aceptan y devuelven JSON salvo las rutas de descarga.

### Formato de un movimiento

El cuerpo mínimo de `POST /registrar` es:

```json
{
  "fecha": "2026-09-01",
  "monto": 151000,
  "referencia": "FV-4001",
  "descripcion": "VENTA TARJETA"
}
```

`fecha` debe usar el formato ISO `AAAA-MM-DD`; `monto` es un entero en
guaraníes y puede ser cero; `referencia` puede estar vacía. La descripción se
usa en el nivel 3 de conciliación. El servicio devuelve `201` si el movimiento
se guarda y `400` si falta `fecha` o `monto`.

### Códigos HTTP y errores

| Código | Significado |
|---:|---|
| `200` | Consulta, conciliación o verificación válida |
| `201` | Movimiento, lote o extracto creado |
| `400` | JSON inválido o campos obligatorios ausentes |
| `404` | Ruta no disponible para el actor |
| `409` | La verificación detectó una alteración o brecha |
| `500` | Error de persistencia o de generación del archivo |

Las respuestas de error tienen la forma:

```json
{"error": "descripción del problema"}
```

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

Ejemplo de una conciliación:

```powershell
curl.exe -X POST http://127.0.0.1:5000/conciliar
curl.exe http://127.0.0.1:5000/resultado
curl.exe http://127.0.0.1:5000/eventos
```

Una respuesta de conciliación tiene dos colecciones:

```json
{
  "pares": [
    {
      "empresa": {"fecha": "2026-09-01", "monto": 151000},
      "banco": {"fecha": "2026-09-01", "monto": 151000},
      "nivel": 1
    }
  ],
  "pendientes": [
    {
      "empresa": {"fecha": "2026-09-01", "monto": 555555},
      "explicacion": "sin candidato"
    }
  ]
}
```

El campo `nivel` permite distinguir coincidencias directas de coincidencias
basadas en fecha o descripción. Un movimiento bancario no puede aparecer en
dos pares de la misma ejecución.

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

- cargar el escenario demo equivalente a la aplicación Python (60 movimientos
  de empresa y 58 del banco) con el botón **Cargar demo 60/58**;
- registrar movimientos de empresa y banco;
- ejecutar la conciliación desde el navegador;
- visualizar cruces por nivel y pendientes;
- cerrar lotes y guardar su huella;
- consultar el historial de eventos;
- exportar toda la memoria como JSON;
- importar una memoria previamente exportada;
- borrar los datos locales del navegador.

El botón **Descargar CSV de empresa y banco** convierte los movimientos de la
memoria web en archivos que pueden abrirse con Excel u otro sistema contable.
La conversión no ejecuta Python en GitHub Pages: traduce en JavaScript las
reglas y el escenario principal del ZIP para que el flujo funcione como sitio
estático.

La memoria se guarda en IndexedDB y mantiene un respaldo en localStorage. Es
intencionalmente local: GitHub Pages sirve archivos estáticos y no ofrece una
base de datos compartida. Para mover datos entre equipos, utiliza **Exportar
memoria** e **Importar memoria**. Para una memoria central multiusuario se
necesitaría añadir una API autenticada y un almacenamiento remoto.

### Publicar el sitio paso a paso

1. Sube los cambios a `main`; el workflow de Pages se ejecuta automáticamente.
2. En GitHub abre **Settings > Pages**.
3. En **Build and deployment**, selecciona **GitHub Actions**.
4. Espera a que finalice el workflow **Publicar ConciliaChain en GitHub
   Pages**.
5. Abre la URL que GitHub muestre en la configuración de Pages.

El workflow no instala paquetes ni construye artefactos: publica directamente
`docs/`. Por eso la URL puede funcionar en un repositorio de usuario o en un
repositorio de proyecto sin cambiar el código de la SPA. Si se utiliza un
dominio propio, la configuración DNS y el archivo `CNAME` deben añadirse según
la configuración de Pages de la organización.

### Memoria, copias y privacidad

La memoria web se identifica por el origen completo (dominio, protocolo y
puerto). Una copia creada en `http://localhost` no aparece automáticamente en
la URL de GitHub Pages. Exporta la memoria desde el origen anterior y luego
impórtala desde el nuevo.

El archivo JSON exportado incluye movimientos, lotes, resultado y eventos. Se
trata de una copia operativa, no de un archivo cifrado: no lo envíes por correo
ni lo subas a un repositorio público si contiene datos reales. Para borrar la
memoria, utiliza el botón **Borrar memoria** y confirma la operación; el borrado
no puede deshacerse salvo que exista una exportación previa.

## Ejemplo programático

El núcleo puede utilizarse sin iniciar servidores:

```python
from datos_prueba.generador import empresa, banco
from nucleo.conciliar import conciliar

pares, pendientes = conciliar(empresa(), banco())
print(f"pares={len(pares)} pendientes={len(pendientes)}")
```

Para una integración propia, transforma cada registro de entrada al formato
`fecha`, `monto`, `referencia` y `descripcion`, conserva los identificadores
del sistema origen en `metadata` y registra los errores sin convertir una
entrada inválida en un movimiento exitoso.

## Diagnóstico rápido

### El puerto ya está ocupado

Detén una ejecución anterior con `Ctrl+C` o cambia el modo de ejecución. Los
puertos forman parte del contrato, por lo que no se recomienda cambiar uno
solo sin actualizar también los clientes que lo consumen.

### La verificación devuelve `409`

Comprueba que:

1. el lote y el actor utilizados en la URL sean los mismos del cierre;
2. el archivo dentro de `datos/<actor>/extractos/` no haya sido editado;
3. exista la cadena `datos/<actor>/cadena.jsonl`;
4. la copia no haya sido truncada o concatenada con otra cadena.

No sobrescribas el archivo para ocultar el error. Conserva la copia inválida
para investigar y genera un lote nuevo después de corregir el origen.

### La web no conserva datos

Verifica que el navegador permita almacenamiento para el dominio de Pages y
que no estés usando una ventana privada con políticas restrictivas. También
puedes comprobar la memoria exportando un JSON antes de cerrar la pestaña.
Si el navegador bloquea IndexedDB, la aplicación intenta utilizar
`localStorage`; si ambos están deshabilitados, usa la exportación manual como
único mecanismo de respaldo.

### No aparecen 55 cruces

Confirma que empresa y banco se hayan cargado desde el mismo dataset
determinista, que no se hayan mezclado movimientos de otra ejecución y que
cada banco se use una sola vez. Las fechas fijas del generador son parte del
escenario de prueba; datos reales pueden producir una cantidad diferente.

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
