/* Memoria de ConciliaChain: IndexedDB, con respaldo transparente en localStorage. */
(function () {
  "use strict";
  const DB = "conciliachain-memoria", STORE = "estado", VERSION = 1;
  const hoy = new Date().toISOString().slice(0, 10);
  const inicial = { empresa: [], banco: [], lotes: [], eventos: [], resultado: null, blockchain: [] };
  let estado = null;

  function clonar(x) { return JSON.parse(JSON.stringify(x)); }
  function canonico(x) { return JSON.stringify(x, Object.keys(x).sort()); }
  async function sha256(texto) {
    const bytes = new TextEncoder().encode(texto);
    const buffer = await crypto.subtle.digest("SHA-256", bytes);
    return Array.from(new Uint8Array(buffer)).map(x => x.toString(16).padStart(2, "0")).join("");
  }
  function contenidoBloque(b) {
    return JSON.stringify({ indice:b.indice, timestamp:b.timestamp, transacciones:b.transacciones,
      hash_anterior:b.hash_anterior, nonce:b.nonce, dificultad:b.dificultad });
  }
  async function minarBloque(indice, transacciones, anterior, dificultad, timestamp) {
    let nonce=0, hash="";
    do { hash=await sha256(contenidoBloque({indice,timestamp,transacciones,hash_anterior:anterior,nonce,dificultad})); nonce++; }
    while (!hash.startsWith("0".repeat(dificultad)));
    return {indice,timestamp,transacciones,hash_anterior:anterior,nonce:nonce-1,dificultad,hash_bloque:hash};
  }
  async function prepararBlockchain() {
    if (estado.blockchain && estado.blockchain.length) return;
    const genesis={indice:0,timestamp:0,transacciones:[],hash_anterior:"0".repeat(64),nonce:0,dificultad:1};
    genesis.hash_bloque=await sha256(contenidoBloque(genesis));
    while(!genesis.hash_bloque.startsWith("0")) genesis.nonce++,genesis.hash_bloque=await sha256(contenidoBloque(genesis));
    estado.blockchain=[genesis]; await guardar();
  }
  async function agregarBloque(transacciones) {
    const anterior=estado.blockchain[estado.blockchain.length-1];
    const bloque=await minarBloque(estado.blockchain.length,transacciones,anterior.hash_bloque,1,Date.now());
    estado.blockchain.push(bloque);
  }
  async function validarBlockchain() {
    if (!estado.blockchain || !estado.blockchain.length) return false;
    for(let i=0;i<estado.blockchain.length;i++) {
      const b=estado.blockchain[i], esperado=await sha256(contenidoBloque(b));
      if(esperado!==b.hash_bloque || !b.hash_bloque.startsWith("0".repeat(b.dificultad))) return false;
      if(i===0 ? b.hash_anterior!=="0".repeat(64) : b.hash_anterior!==estado.blockchain[i-1].hash_bloque) return false;
    }
    return true;
  }
  function abrir() {
    return new Promise((resolve) => {
      if (!window.indexedDB) return resolve(null);
      const req = indexedDB.open(DB, VERSION);
      req.onupgradeneeded = () => req.result.createObjectStore(STORE);
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => resolve(null);
    });
  }
  async function leer() {
    const respaldo = localStorage.getItem(DB);
    try {
      const db = await abrir();
      if (!db) return respaldo ? JSON.parse(respaldo) : clonar(inicial);
      return await new Promise((resolve) => {
        const r = db.transaction(STORE).objectStore(STORE).get("estado");
        r.onsuccess = () => resolve(r.result || (respaldo ? JSON.parse(respaldo) : clonar(inicial)));
        r.onerror = () => resolve(respaldo ? JSON.parse(respaldo) : clonar(inicial));
      });
    } catch (_) { return respaldo ? JSON.parse(respaldo) : clonar(inicial); }
  }
  async function guardar() {
    localStorage.setItem(DB, JSON.stringify(estado));
    const db = await abrir();
    if (!db) return;
    await new Promise((resolve) => {
      const tx = db.transaction(STORE, "readwrite");
      tx.objectStore(STORE).put(clonar(estado), "estado");
      tx.oncomplete = resolve; tx.onerror = resolve;
    });
  }
  function aviso(texto, tipo="ok") {
    const el = document.querySelector("#aviso"); el.textContent = texto;
    el.className = "aviso visible " + tipo; window.clearTimeout(aviso.timer);
    aviso.timer = window.setTimeout(() => el.className = "aviso", 4500);
  }
  function id() { return crypto.randomUUID ? crypto.randomUUID() : Date.now()+"-"+Math.random(); }
  function monto(x) { return Number(x || 0).toLocaleString("es-PY") + " Gs."; }
  function hash(texto) { let h=2166136261; for(let i=0;i<texto.length;i++) h=Math.imul(h^texto.charCodeAt(i),16777619); return ("00000000"+(h>>>0).toString(16)).slice(-8); }
  function renderResumen() {
    document.querySelector("#totalEmpresa").textContent=estado.empresa.length;
    document.querySelector("#totalBanco").textContent=estado.banco.length;
    document.querySelector("#totalPares").textContent=estado.resultado ? estado.resultado.pares.length : 0;
    document.querySelector("#totalPendientes").textContent=estado.resultado ? estado.resultado.pendientes.length : 0;
  }
  function conciliar() {
    const usados = new Set(), pares=[], pendientes=[];
    estado.empresa.forEach(a => {
      let elegido=null, nivel=0;
      for (let i=0;i<estado.banco.length;i++) { const b=estado.banco[i]; if(usados.has(i)) continue;
        if(a.referencia && a.referencia.trim().toUpperCase()===String(b.referencia||"").trim().toUpperCase() && Number(a.monto)===Number(b.monto)){elegido=i;nivel=1;break;}
      }
      if(elegido===null) for(let i=0;i<estado.banco.length;i++){const b=estado.banco[i];if(usados.has(i)||Number(a.monto)!==Number(b.monto))continue;const dias=Math.abs((new Date(a.fecha)-new Date(b.fecha))/86400000);if(dias<=3){elegido=i;nivel=2;break;}}
      if(elegido===null) for(let i=0;i<estado.banco.length;i++){const b=estado.banco[i];if(usados.has(i))continue;const comunes=(a.descripcion||"").toUpperCase().split(/\s+/).filter(x=>(b.descripcion||"").toUpperCase().includes(x)&&x.length>3);if(comunes.length&&Math.abs(Number(a.monto)-Number(b.monto))<=Number(a.monto)*.05){elegido=i;nivel=3;break;}}
      if(elegido===null) pendientes.push({empresa:a,explicacion:"Sin candidato"}); else {usados.add(elegido);pares.push({empresa:a,banco:estado.banco[elegido],nivel});}
    });
    estado.banco.forEach((b,i)=>{if(!usados.has(i))pendientes.push({banco:b,explicacion:"Sin candidato"});});
    estado.resultado={pares,pendientes,fecha:new Date().toISOString()}; estado.eventos.push({tipo:"conciliacion_ejecutada",fecha:estado.resultado.fecha,pares:pares.length});
    agregarBloque([{tipo:"conciliacion_ejecutada",pares:pares.length,pendientes:pendientes.length,fecha:estado.resultado.fecha}]).then(()=>guardar()).then(()=>{render();aviso(`Conciliación completada: ${pares.length} cruces y ${pendientes.length} pendientes.`);});
  }
  function renderResultado() {
    const el=document.querySelector("#resultado");
    if(!estado.resultado)return el.className="tabla-vacia",el.textContent="Todavía no ejecutaste una conciliación.";
    const filas=estado.resultado.pares.map(x=>`<tr><td>${x.empresa.referencia||"Sin referencia"}</td><td>${monto(x.empresa.monto)}</td><td>${x.banco.fecha}</td><td><span class="etiqueta nivel-${x.nivel}">Nivel ${x.nivel}</span></td></tr>`);
    const pendientes=estado.resultado.pendientes.map(x=>`<tr><td>${x.empresa?.referencia||x.banco?.referencia||"Sin referencia"}</td><td>${monto((x.empresa||x.banco).monto)}</td><td colspan="2"><span class="etiqueta pendiente">${x.explicacion}</span></td></tr>`);
    el.innerHTML=`<table class="tabla"><thead><tr><th>Referencia</th><th>Monto</th><th>Fecha banco</th><th>Resultado</th></tr></thead><tbody>${filas.join("")}${pendientes.join("")}</tbody></table>`;
  }
  function renderMovimientos() {
    const filas=["empresa","banco"].flatMap(a=>estado[a].map(x=>`<tr><td>${a}</td><td>${x.fecha}</td><td>${monto(x.monto)}</td><td>${x.referencia||"-"}</td><td>${x.descripcion||"-"}</td></tr>`));
    document.querySelector("#listaMovimientos").innerHTML=`<table class="tabla"><thead><tr><th>Actor</th><th>Fecha</th><th>Monto</th><th>Referencia</th><th>Descripción</th></tr></thead><tbody>${filas.join("")}</tbody></table>`;
  }
  function renderLotes() {
    document.querySelector("#listaLotes").innerHTML=estado.lotes.length?estado.lotes.map(x=>`<div class="fila-lista"><span><strong>${x.lote}</strong> · ${x.actor}</span><span>${x.cantidad} movimientos · huella ${x.huella}</span></div>`).join(""):"<p class='tabla-vacia'>No hay lotes cerrados.</p>";
    document.querySelector("#listaEventos").innerHTML=estado.eventos.length?estado.eventos.slice().reverse().map(x=>`<div class="fila-lista"><span>${x.tipo}</span><small>${new Date(x.fecha).toLocaleString("es-PY")}</small></div>`).join(""):"<p class='tabla-vacia'>No hay eventos.</p>";
  }
  async function renderBlockchain() {
    const valido=await validarBlockchain();
    const estadoEl=document.querySelector("#estadoBlockchain"); estadoEl.textContent=valido?"Cadena válida":"Cadena alterada"; estadoEl.className="etiqueta "+(valido?"nivel-1":"pendiente");
    document.querySelector("#resumenBlockchain").textContent=`${estado.blockchain.length} bloques · SHA-256 · prueba de trabajo dificultad 1 · ${valido?"integridad confirmada":"requiere revisión"}`;
    document.querySelector("#listaBlockchain").innerHTML=estado.blockchain.slice().reverse().map(b=>`<article class="bloque ${b.indice===0?"genesis":""}"><strong>Bloque #${b.indice}${b.indice===0?" · GÉNESIS":""}</strong><span>${b.transacciones.length} transacciones · nonce ${b.nonce}</span><code>hash: ${b.hash_bloque}</code><code>anterior: ${b.hash_anterior}</code></article>`).join("");
  }
  function render(){renderResumen();renderResultado();renderMovimientos();renderLotes();renderBlockchain();}
  async function cerrarLote(e){e.preventDefault();const f=new FormData(e.target),actor=f.get("actor"),lote=f.get("lote"),movs=estado[actor];const huella=await sha256(JSON.stringify(movs));estado.lotes.push({actor,lote,cantidad:movs.length,huella,fecha:new Date().toISOString()});estado.eventos.push({tipo:"lote_emitido",actor,lote,fecha:new Date().toISOString()});await agregarBloque([{tipo:"lote_emitido",actor,lote,cantidad:movs.length,huella}]);await guardar();render();aviso(`Lote ${lote} cerrado y añadido al bloque ${estado.blockchain.length-1}.`);}
  async function registrar(e){e.preventDefault();const f=new FormData(e.target),actor=f.get("actor"),movimiento={id:id(),fecha:f.get("fecha"),monto:Number(f.get("monto")),referencia:f.get("referencia"),descripcion:f.get("descripcion")};estado[actor].push(movimiento);estado.eventos.push({tipo:"movimiento_registrado",actor,fecha:new Date().toISOString()});await agregarBloque([{tipo:"movimiento_registrado",actor,movimiento}]);await guardar();render();e.target.reset();e.target.fecha.value=hoy;aviso("Movimiento guardado y registrado en la blockchain local.");}
  function descargar(nombre,contenido,tipo){const a=document.createElement("a");a.href=URL.createObjectURL(new Blob([contenido],{type:tipo}));a.download=nombre;a.click();URL.revokeObjectURL(a.href);}
  function exportar(){descargar("conciliachain-memoria.json",JSON.stringify(estado,null,2),"application/json");}
  function importar(e){const f=e.target.files[0];if(!f)return;const r=new FileReader();r.onload=()=>{try{const x=JSON.parse(r.result);if(!x.empresa||!x.banco)throw Error("estructura");estado=x;guardar().then(()=>{render();aviso("Memoria importada correctamente.");});}catch(_){aviso("El archivo no contiene una memoria válida.","error");}};r.readAsText(f);}
  async function iniciar(){estado=await leer();estado.blockchain=estado.blockchain||[];await prepararBlockchain();document.querySelector("#movimientoForm").fecha.value=hoy;document.querySelector("#conciliar").onclick=conciliar;document.querySelector("#movimientoForm").onsubmit=registrar;document.querySelector("#loteForm").onsubmit=cerrarLote;document.querySelector("#exportarMemoria").onclick=exportar;document.querySelector("#importarMemoria").onchange=importar;document.querySelector("#borrarMemoria").onclick=()=>{if(confirm("¿Borrar todos los datos locales?")){estado=clonar(inicial);prepararBlockchain().then(()=>{render();aviso("Memoria borrada.");});}};document.querySelectorAll("[data-tab]").forEach(b=>b.onclick=()=>{document.querySelectorAll("[data-tab]").forEach(x=>x.classList.remove("activa"));b.classList.add("activa");document.querySelectorAll(".panel").forEach(x=>x.classList.add("oculto"));document.querySelector("#"+b.dataset.tab).classList.remove("oculto");});render();}
  iniciar();
})();
