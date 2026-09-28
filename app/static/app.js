const COLOR_LINEA = {
  "Roja":"var(--l-roja)", "Amarilla":"var(--l-amarilla)", "Verde":"var(--l-verde)",
  "Azul":"var(--l-azul)", "Naranja":"var(--l-naranja)", "Blanca":"var(--l-blanca)",
  "Celeste":"var(--l-celeste)", "Morada":"var(--l-morada)", "Cafe":"var(--l-cafe)"
};
// version resuelta (vis-network no entiende var(--x) dentro de su propio canvas)
const HEX_LINEA = {
  "Roja":"#d6303c", "Amarilla":"#f2c94c", "Verde":"#2e9e5b", "Azul":"#3d7bf0",
  "Naranja":"#f2994a", "Blanca":"#f2f2f2", "Celeste":"#56ccf2", "Morada":"#9b51e0",
  "Cafe":"#8b5e3c"
};

let grafoActual = null;
let network = null;
let nodesDataSet, edgesDataSet;

async function cargarGrafo(){
  const r = await fetch('/api/grafo');
  const d = await r.json();
  grafoActual = d.grafo;
  // Primero lo que no depende de la libreria del mapa, para que los selects siempre se llenen
  llenarSelects(grafoActual);
  dibujarLeyenda(grafoActual);
  dibujarListaEstaciones(grafoActual);
  try{
    dibujarRed(grafoActual);
  }catch(e){
    console.error('No se pudo dibujar el mapa:', e);
    document.getElementById('red-grafo').innerHTML =
      '<p style="padding:1rem">No se pudo cargar el mapa (libreria vis-network). Revisa tu conexion a internet y recarga con Ctrl+F5.</p>';
  }
}

function dibujarLeyenda(g){
  const lineas = [...new Set(g.aristas.map(a => a.linea).filter(Boolean))];
  const cont = document.getElementById('leyenda-lineas');
  cont.innerHTML = lineas.map(l =>
    `<span><span class="pt" style="background:${HEX_LINEA[l] || '#888'}"></span>${l}</span>`
  ).join('');
}

function dibujarListaEstaciones(g){
  const cont = document.getElementById('lista-estaciones');
  cont.innerHTML = g.vertices
    .sort((a,b)=> a.id.localeCompare(b.id))
    .map(v => `<div style="padding:.4rem 0;border-bottom:1px solid var(--borde);">
        <strong>${v.id}</strong> — ${v.nombre}
        <div class="subtexto">${v.descripcion || ''}</div>
      </div>`).join('');
}

function dibujarRed(g, resaltarAristas=null, resaltarNodos=null){
  const nodos = g.vertices.map(v => ({
    id: v.id,
    label: v.nombre,
    title: v.descripcion,
    shape: 'dot',
    size: 14,
    color: (resaltarNodos && resaltarNodos.includes(v.id)) ? '#e3a857' : '#c9d3ea',
    font: { color:'#e9e6dd', size:13 }
  }));
  const aristas = g.aristas.map(a => {
    const enRuta = resaltarAristas && resaltarAristas.some(([o,d]) =>
      (o===a.origen && d===a.destino) || (o===a.destino && d===a.origen));
    return {
      from: a.origen, to: a.destino,
      label: String(a.peso),
      color: { color: enRuta ? '#e3a857' : (HEX_LINEA[a.linea] || '#5a6a90') },
      width: enRuta ? 4 : 2,
      font: { color:'#9aa6c3', size:10, strokeWidth:0 },
      smooth: false
    };
  });

  nodesDataSet = new vis.DataSet(nodos);
  edgesDataSet = new vis.DataSet(aristas);
  const contenedor = document.getElementById('red-grafo');
  const datos = { nodes: nodesDataSet, edges: edgesDataSet };
  const opciones = {
    physics: { stabilization: true, barnesHut: { gravitationalConstant: -6000, springLength: 110 } },
    interaction: { hover: true }
  };
  network = new vis.Network(contenedor, datos, opciones);
}

function llenarSelects(g){
  const opciones = g.vertices
    .sort((a,b)=> a.id.localeCompare(b.id))
    .map(v => `<option value="${v.id}">${v.id} — ${v.nombre}</option>`).join('');
  ['sel-origen','sel-destino','sel-dfs-inicio','sel-bfs-inicio','sel-prim-inicio',
   'ar-origen','ar-destino','del-origen','del-destino'].forEach(id => {
    document.getElementById(id).innerHTML = opciones;
  });
}

function mostrarResultado(elId, texto, esError=false){
  const el = document.getElementById(elId);
  el.className = 'resultado' + (esError ? ' error' : '');
  el.textContent = texto;
}

// ---- Tabs ----
document.querySelectorAll('.tabs button').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tabs button').forEach(b => b.classList.remove('activo'));
    btn.classList.add('activo');
    const tab = btn.dataset.tab;
    document.querySelectorAll('.tab-panel').forEach(p => {
      p.classList.toggle('oculto', p.dataset.panel !== tab);
    });
  });
});

// ---- Dijkstra ----
document.getElementById('btn-dijkstra').addEventListener('click', async () => {
  const origen = document.getElementById('sel-origen').value;
  const destino = document.getElementById('sel-destino').value;
  const r = await fetch(`/api/dijkstra?origen=${origen}&destino=${destino}`);
  const d = await r.json();
  const el = document.getElementById('res-dijkstra');
  if(!d.ok){ mostrarResultado('res-dijkstra', d.error, true); return; }
  const res = d.resultado;
  if(!res.camino){
    mostrarResultado('res-dijkstra', 'No existe un camino entre estas estaciones.', true);
    return;
  }
  const nombres = res.camino.map(id => grafoActual.vertices.find(v=>v.id===id).nombre);
  el.className = 'resultado';
  el.innerHTML = `<div class="costo-grande">${res.costo.toFixed(1)} min</div>` +
    `Ruta: ${res.camino.map((id,i)=>`${id} (${nombres[i]})`).join(' → ')}`;

  const paresRuta = [];
  for(let i=0;i<res.camino.length-1;i++) paresRuta.push([res.camino[i], res.camino[i+1]]);
  dibujarRed(grafoActual, paresRuta, res.camino);
});

// ---- DFS ----
document.getElementById('btn-dfs').addEventListener('click', async () => {
  const inicio = document.getElementById('sel-dfs-inicio').value;
  const r = await fetch(`/api/dfs?inicio=${inicio}`);
  const d = await r.json();
  if(!d.ok){ mostrarResultado('res-dfs', d.error, true); return; }
  const res = d.resultado;
  mostrarResultado('res-dfs',
    `Orden de visita:\n${res.orden.join(' -> ')}\n\n` +
    `Aristas usadas: ${res.aristas.map(([a,b])=>`${a}-${b}`).join(', ')}\n\n` +
    (res.no_alcanzables.length ? `No alcanzables: ${res.no_alcanzables.join(', ')}` : 'Todos los nodos son alcanzables.')
  );
  dibujarRed(grafoActual, res.aristas, res.orden);
});

// ---- BFS ----
document.getElementById('btn-bfs').addEventListener('click', async () => {
  const inicio = document.getElementById('sel-bfs-inicio').value;
  const r = await fetch(`/api/bfs?inicio=${inicio}`);
  const d = await r.json();
  if(!d.ok){ mostrarResultado('res-bfs', d.error, true); return; }
  const res = d.resultado;
  const aristasArbol = Object.entries(res.padre)
    .filter(([hijo,padre]) => padre !== null)
    .map(([hijo,padre]) => [padre, hijo]);
  mostrarResultado('res-bfs',
    `Orden por niveles:\n${res.orden.join(' -> ')}\n\n` +
    `Niveles: ${JSON.stringify(res.nivel)}\n\n` +
    (res.no_alcanzables.length ? `No alcanzables: ${res.no_alcanzables.join(', ')}` : 'Todos los nodos son alcanzables.')
  );
  dibujarRed(grafoActual, aristasArbol, res.orden);
});

// ---- MST (Kruskal + Prim) ----
document.getElementById('btn-mst').addEventListener('click', async () => {
  const inicio = document.getElementById('sel-prim-inicio').value;
  const [rk, rp] = await Promise.all([
    fetch('/api/kruskal'), fetch(`/api/prim?inicio=${inicio}`)
  ]);
  const dk = await rk.json(), dp = await rp.json();
  if(!dk.ok){ mostrarResultado('res-mst', dk.error, true); return; }
  if(!dp.ok){ mostrarResultado('res-mst', dp.error, true); return; }
  const k = dk.resultado, p = dp.resultado;
  const el = document.getElementById('res-mst');
  el.className = 'resultado';
  el.innerHTML = `
    <strong>Kruskal</strong> — costo total: ${k.costo_total.toFixed(1)} min
    (${k.aceptadas.length} aristas, ${k.rechazadas.length} rechazadas por ciclo)<br>
    <strong>Prim</strong> (desde ${p.nodo_inicial}) — costo total: ${p.costo_total.toFixed(1)} min
    (${p.aristas.length} aristas)<br><br>
    ${Math.abs(k.costo_total - p.costo_total) < 1e-6
      ? 'Ambos coinciden en el costo total.'
      : 'Los costos difieren, revisar implementación.'}
  `;
  const aristasKruskal = k.aceptadas.map(a => [a.origen, a.destino]);
  dibujarRed(grafoActual, aristasKruskal);
});

// ---- Matriz / lista ----
document.getElementById('btn-matriz').addEventListener('click', async () => {
  const r = await fetch('/api/matriz');
  const d = await r.json();
  const el = document.getElementById('res-datos');
  let html = '<table><tr><th></th>' + d.ids.map(i=>`<th>${i}</th>`).join('') + '</tr>';
  d.ids.forEach((fila, i) => {
    html += `<tr><th>${fila}</th>` + d.matriz[i].map(v => `<td>${v || ''}</td>`).join('') + '</tr>';
  });
  html += '</table>';
  el.className = 'resultado';
  el.innerHTML = html;
});

document.getElementById('btn-lista').addEventListener('click', async () => {
  const r = await fetch('/api/lista_adyacencia');
  const d = await r.json();
  const texto = Object.entries(d.lista)
    .map(([nodo, vecinos]) => `${nodo}: ${vecinos.map(([v,p,l])=>`${v}(${p}min)`).join(', ')}`)
    .join('\n');
  mostrarResultado('res-datos', texto);
});

// ---- Reporte ----
document.getElementById('btn-reporte').addEventListener('click', async () => {
  const origen = document.getElementById('sel-origen').value;
  const destino = document.getElementById('sel-destino').value;
  const r = await fetch(`/api/reporte?origen=${origen}&destino=${destino}`);
  const d = await r.json();
  if(!d.ok){ mostrarResultado('res-reporte', d.error, true); return; }
  mostrarResultado('res-reporte', d.reporte);
});

// ---- Admin: agregar/eliminar ----
document.getElementById('btn-add-vertice').addEventListener('click', async () => {
  const body = {
    id: document.getElementById('nv-id').value,
    nombre: document.getElementById('nv-nombre').value,
    descripcion: document.getElementById('nv-desc').value
  };
  const r = await fetch('/api/vertices', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)});
  const d = await r.json();
  if(!d.ok){ mostrarResultado('res-admin', d.error, true); return; }
  grafoActual = d.grafo;
  dibujarRed(grafoActual); llenarSelects(grafoActual); dibujarListaEstaciones(grafoActual);
  mostrarResultado('res-admin', 'Vértice agregado correctamente.');
});

document.getElementById('btn-add-arista').addEventListener('click', async () => {
  const body = {
    origen: document.getElementById('ar-origen').value,
    destino: document.getElementById('ar-destino').value,
    peso: document.getElementById('ar-peso').value,
    linea: document.getElementById('ar-linea').value
  };
  const r = await fetch('/api/aristas', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)});
  const d = await r.json();
  if(!d.ok){ mostrarResultado('res-admin', d.error, true); return; }
  grafoActual = d.grafo;
  dibujarRed(grafoActual); dibujarLeyenda(grafoActual);
  mostrarResultado('res-admin', 'Arista agregada correctamente.');
});

document.getElementById('btn-del-arista').addEventListener('click', async () => {
  const body = {
    origen: document.getElementById('del-origen').value,
    destino: document.getElementById('del-destino').value
  };
  const r = await fetch('/api/aristas', {method:'DELETE', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)});
  const d = await r.json();
  if(!d.ok){ mostrarResultado('res-admin', d.error, true); return; }
  grafoActual = d.grafo;
  dibujarRed(grafoActual);
  mostrarResultado('res-admin', 'Arista eliminada correctamente.');
});

document.getElementById('btn-reiniciar').addEventListener('click', async () => {
  const r = await fetch('/api/reiniciar', {method:'POST'});
  const d = await r.json();
  grafoActual = d.grafo;
  dibujarRed(grafoActual); llenarSelects(grafoActual); dibujarLeyenda(grafoActual); dibujarListaEstaciones(grafoActual);
  mostrarResultado('res-admin', 'Red reiniciada a los datos originales (vertices.csv / aristas.csv).');
});

cargarGrafo();


  (function(){
    const wrap = document.getElementById('heroWrap');
    const fondo = document.getElementById('heroFondo');
    const frente = document.getElementById('heroFrente');

    function actualizar(){
      const total = wrap.offsetHeight - window.innerHeight;
      let p = -wrap.getBoundingClientRect().top / total;
      p = Math.min(Math.max(p, 0), 1);

      fondo.style.transform  = `translateY(${p * 8}vh) scale(${1 + p * 0.08})`; // se mueve poco
      frente.style.transform = `translateY(${-p * 55}vh)`;                       // sube más y tapa el texto
    }
    window.addEventListener('scroll', actualizar, {passive:true});
    window.addEventListener('resize', actualizar);
    actualizar();
  })();