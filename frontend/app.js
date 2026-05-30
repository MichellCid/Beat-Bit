const API_URL = "http://localhost:8000/api";
let chartInstance = null;
let idArtistaActual = null;
let graficaArtista = null;

function mostrarSeccion(id) {
    document.querySelectorAll("#inicio, #paises, #artistas, #historico").forEach(sec => {
        sec.style.display = "none";
    });
    document.getElementById(id).style.display = "block";
}

async function cargarTopGlobal() {
    const errorMsg = document.getElementById("errorMensajeGlobal");
    if(errorMsg) {
        errorMsg.style.display = "none";
        errorMsg.textContent = "";
    }

    try {
        const response = await fetch(`${API_URL}/top-global`);
        if (!response.ok) throw new Error("Falla en el servidor");
        const data = await response.json();
        
        localStorage.setItem("cache_top_global", JSON.stringify(data));
        renderizarDashboardGlobal(data);

        /** //document.getElementById("artistaNum1").textContent =
          //  data.artista_top.nombre;

        const imagen = document.getElementById("imagenArtistaNum1");

        if (imagen) {
            imagen.src = data.artista_top.imagen || "https://via.placeholder.com/180?text=Sin+Imagen";
            imagen.alt = data.artista_top.nombre || "Sin Imagen";
        }

        const tbody = document.querySelector("#tablaTopMundial tbody");
        
        if(tbody) {
            tbody.innerHTML = "";

            data.top_global
                .sort((a, b) => Number(b.reproducciones) - Number(a.reproducciones))
                .forEach((track, index) => {
                    tbody.innerHTML += `
                        <tr>
                            <td>${index + 1}</td>
                            <td>${track.nombre_cancion}</td>
                            <td>${track.nombre_artista}</td>
                            <td>${Number(track.reproducciones).toLocaleString()}</td>
                        </tr>
                    `;
                });
        }**/

    } catch (error) {
        console.error("Error cargando top global:", error);
        if(errorMsg) {
            errorMsg.style.display = "block";
            errorMsg.textContent = "Error al cargar las métricas. Mostrando la última versión disponible.";
        }
        
        const cacheData = localStorage.getItem("cache_top_global");
        if (cacheData) {
            renderizarDashboardGlobal(JSON.parse(cacheData));
        }
    }
}

function renderizarDashboardGlobal(data) {
    const pistas = data.top_global.sort((a, b) => Number(b.reproducciones) - Number(a.reproducciones));
    
    if (data.artista_top) {
        document.getElementById("artistaNum1").textContent = data.artista_top.nombre;
        const imagen = document.getElementById("imagenArtistaNum1");
        
        if (imagen) {
            if (data.artista_top.imagen) {
                imagen.src = data.artista_top.imagen;
            } else {
                imagen.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(data.artista_top.nombre)}&background=3498db&color=fff&size=120`;
            }
            imagen.alt = data.artista_top.nombre;
        }
    }

    if (pistas.length > 0) {
        const topTrack = pistas[0];
        document.getElementById("cancionNum1").textContent = topTrack.nombre_cancion;
        document.getElementById("artistaCancionNum1").textContent = topTrack.nombre_artista;
        document.getElementById("albumNum1").textContent = `${topTrack.nombre_cancion} - Single`; 
    }

    const leaderboard = document.getElementById("leaderboardTopMundial");
    if(leaderboard) {
        leaderboard.innerHTML = "";
        pistas.slice(0, 10).forEach((track, index) => {
            const rank = index + 1;
            const rankStr = rank < 10 ? `0${rank}` : rank;
            const rankClass = rank <= 3 ? `top-${rank}` : '';
            const avatarUrl = `https://ui-avatars.com/api/?name=${encodeURIComponent(track.nombre_artista)}&background=1a1a1a&color=fff&size=60`;

                    leaderboard.innerHTML += `
                        <div class="leaderboard-row ${rankClass}">
                            <div class="leaderboard-left">
                                <div class="rank-number">${rankStr}</div>
                                <img src="${avatarUrl}" class="leaderboard-avatar" alt="Avatar de ${track.nombre_artista}">
                                <div class="leaderboard-info">
                                    <div class="leaderboard-title">${track.nombre_cancion.toUpperCase()}</div>
                                    <div class="leaderboard-artist">👤 ${track.nombre_artista}</div>
                                </div>
                            </div>
                            <div class="leaderboard-right">
                                <div class="leaderboard-score-box">
                                    <span class="score-label">REPRODUCCIONES</span>
                                    <span class="score-value">${Number(track.reproducciones).toLocaleString()}</span>
                                </div>
                            </div>
                        </div>
                    `;
        });
    }
}


function mostrarMensajePais(text) {
    const mensaje = document.getElementById("mensajePais");
    if (mensaje) {
        mensaje.textContent = text || "";
    }
}

async function cargarPaisesDisponibles() {
    try {
        const response = await fetch(`${API_URL}/paises`);
        const data = await response.json();

        const select = document.getElementById("selectPais");
        if (!select) return;

        select.innerHTML = `<option value="">Todos los países</option>`;
        data.paises.forEach(pais => {
            select.innerHTML += `<option value="${pais}">${pais}</option>`;
        });

        select.addEventListener("change", () => {
            cargarTopPaises(select.value);
            cargarCiudadesDisponible(select.value);
        });

        const btnLimpiar = document.getElementById("btnLimpiarPais");
        if (btnLimpiar) {
            btnLimpiar.addEventListener("click", () => {
                select.value = "";
                cargarTopPaises();
                ocultarCiudades();
            });
        }
    } catch (error) {
    }
}

function mostrarMensajeCiudad(text) {
    const mensaje = document.getElementById("mensajeCiudad");
    if (mensaje) {
        mensaje.textContent = text || "";
    }
}

function ocultarCiudades() {
    const section = document.getElementById("ciudadSection");
    if (section) {
        section.style.display = "none";
    }
    const tbody = document.querySelector("#tablaTopCiudad tbody");
    if (tbody) tbody.innerHTML = "";
    mostrarMensajeCiudad("");
}

async function cargarCiudadesDisponible(pais) {
    if (!pais) {
        ocultarCiudades();
        return;
    }

    try {
        const response = await fetch(`${API_URL}/ciudades?country=${encodeURIComponent(pais)}`);
        const data = await response.json();

        const section = document.getElementById("ciudadSection");
        const select = document.getElementById("selectCiudad");
        const dataList = document.getElementById("ciudadesDatalist");
        const input = document.getElementById("inputCiudad");

        if (!section || !select || !dataList || !input) return;

        const cities = data.ciudades || [];
        if (!cities.length) {
            section.style.display = "none";
            return;
        }

        section.style.display = "block";
        select.innerHTML = `<option value="">Elige una ciudad</option>`;
        dataList.innerHTML = "";

        cities.forEach(ciudad => {
            select.innerHTML += `<option value="${ciudad}">${ciudad}</option>`;
            dataList.innerHTML += `<option value="${ciudad}"></option>`;
        });

        select.onchange = () => {
            if (select.value) {
                input.value = select.value;
                cargarTopCiudad(document.getElementById("selectPais").value, select.value);
            }
        };

        const btnLimpiarCiudad = document.getElementById("btnLimpiarCiudad");
        if (btnLimpiarCiudad) {
            btnLimpiarCiudad.onclick = () => {
                select.value = "";
                input.value = "";
                ocultarCiudades();
                cargarTopPaises(document.getElementById("selectPais").value);
            };
        }

        const btnBuscarCiudad = document.getElementById("btnBuscarCiudad");
        if (btnBuscarCiudad) {
            btnBuscarCiudad.onclick = () => {
                const selectedCiudad = select.value.trim();
                const typedCiudad = input.value.trim();
                const ciudad = typedCiudad || selectedCiudad;
                if (ciudad) {
                    const paisSeleccionado = document.getElementById("selectPais").value;
                    cargarTopCiudad(paisSeleccionado, ciudad);
                    select.value = ciudad;
                    input.value = ciudad;
                }
            };
        }
    } catch (error) {
    }
}

async function cargarTopPaises(pais = "") {
    try {
        mostrarMensajePais("");
        mostrarMensajeCiudad("");
        const url = pais
            ? `${API_URL}/top-paises?country=${encodeURIComponent(pais)}`
            : `${API_URL}/top-paises`;

        const response = await fetch(url);
        const data = await response.json();

        const tbody = document.querySelector("#tablaTopPaises tbody");
        tbody.innerHTML = "";

        if (!data.top_paises || data.top_paises.length === 0) {
            if (pais) {
                mostrarMensajePais("Sin datos registrados para esta región");
            }
            return;
        }

        data.top_paises.forEach(track => {
            tbody.innerHTML += `
                <tr>
                    <td>${track.pais || "-"}</td>
                    <td>${track.nombre_cancion}</td>
                    <td>${track.nombre_artista}</td>
                    <td>${Number(track.reproducciones).toLocaleString()}</td>
                </tr>
            `;
        });
    } catch (error) {
        mostrarMensajePais("Ocurrió un error al cargar los datos del país.");
    }
}

async function cargarTopCiudad(pais, ciudad) {
    if (!pais || !ciudad) {
        mostrarMensajeCiudad("Selecciona un país y una ciudad para ver el ranking local.");
        return;
    }

    try {
        mostrarMensajeCiudad("");
        const response = await fetch(`${API_URL}/top-ciudad?country=${encodeURIComponent(pais)}&city=${encodeURIComponent(ciudad)}`);
        const data = await response.json();

        const tbody = document.querySelector("#tablaTopCiudad tbody");
        tbody.innerHTML = "";

        if (!data.top_ciudad || data.top_ciudad.length === 0) {
            mostrarMensajeCiudad("No hay rankings disponibles para esta ciudad");
            return;
        }

        data.top_ciudad.slice(0, 10).forEach((track, index) => {
            tbody.innerHTML += `
                <tr>
                    <td>${index + 1}</td>
                    <td>${track.nombre_cancion}</td>
                    <td>${track.nombre_artista}</td>
                    <td>${Number(track.reproducciones).toLocaleString()}</td>
                </tr>
            `;
        });
    } catch (error) {
        mostrarMensajeCiudad("No hay rankings disponibles para esta ciudad");
    }
}

async function cargarHistorico() {
    const inputInicio = document.getElementById("anioInicio").value;
    const inputFin = document.getElementById("anioFin").value;
    const mensajeError = document.getElementById("mensajeHistorico");

    mensajeError.style.display = "none";

    let anioFin = inputFin ? parseInt(inputFin) : new Date().getFullYear();
    let anioInicio = inputInicio ? parseInt(inputInicio) : anioFin - 5; 

    try {
        const response = await fetch(`${API_URL}/historico?inicio=${anioInicio}&fin=${anioFin}`);
        const data = await response.json();

        if (!data.evolucion || data.evolucion.length === 0) {
            mensajeError.textContent = "Error: No hay datos para el periodo";
            mensajeError.style.display = "block";
            if (chartInstance) chartInstance.destroy();
            return;
        }

        renderizarGraficaHistorico(data.evolucion);
    } catch (error) {
        mensajeError.textContent = "Error al conectar con el servidor.";
        mensajeError.style.display = "block";
    }
}

function renderizarGraficaHistorico(datos) {
    const ctx = document.getElementById('graficaHistorico').getContext('2d');
    
    if (chartInstance) {
        chartInstance.destroy(); 
    }

    const etiquetasAnios = datos.map(d => d.anio);
    const generos = Object.keys(datos[0]).filter(key => key !== 'anio');
    const colores = ['#3498db', '#e74c3c', '#2ecc71', '#f1c40f', '#9b59b6'];

    const datasets = generos.map((genero, index) => ({
        label: genero.charAt(0).toUpperCase() + genero.slice(1),
        data: datos.map(d => d[genero]),
        borderColor: colores[index % colores.length],
        backgroundColor: colores[index % colores.length],
        fill: false,
        tension: 0.3,
        borderWidth: 2
    }));

    chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: etiquetasAnios,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: '#ffffff' } }
            },
            scales: {
                x: { ticks: { color: '#aaaaaa' }, grid: { color: '#333333' } },
                y: { ticks: { color: '#aaaaaa' }, grid: { color: '#333333' } }
            }
        }
    });
}




//-----------------------------------------------------------------------------------------------------------------------------
// funciones para la pantalla de artistas

async function infoCantante(artista, topAlbum=null){
    document.getElementById("nombrePerfilArtista").textContent = artista.nombre;
    document.getElementById("imagenPerfilArtista").src = artista.imagen || "https://via.placeholder.com/180?text=Sin+Imagen";
    document.getElementById("imagenPerfilArtista").alt = artista.nombre || "Sin Imagen";
    
    document.getElementById("seguidoresArtista").textContent = Number(artista.seguidores ?? 0).toLocaleString();
    document.getElementById("popularidadArtista").textContent = artista.popularidad ?? "0";
    
    document.getElementById("generosArtista").textContent = (artista.generos && artista.generos.length > 0) ? artista.generos.join(", ") : "No especificados";
        
    document.getElementById("mejorAlbumArtista").textContent = artista.mejor_album;
    const imgAlbum = document.getElementById("imagenMejorAlbum");
    if (imgAlbum) {
        imgAlbum.src = artista.imagen_album || "https://via.placeholder.com/180?text=Sin+Imagen";
        imgAlbum.alt = artista.mejor_album;
    }

    const elementoCancion = document.getElementById("mejorCancionArtista");
    if (elementoCancion) {
        elementoCancion.textContent = artista.mejor_cancion;
    }

    /** if (topAlbum) {
        document.getElementById("mejorAlbumArtista").textContent = topAlbum.nombre || "No disponible";
        document.getElementById("imagenMejorAlbum").src = topAlbum.imagen ?? "https://via.placeholder.com/180?text=Sin+Imagen";
        document.getElementById("imagenMejorAlbum").alt = topAlbum.nombre ?? "Sin Imagen";
    } else {
        document.getElementById("mejorAlbumArtista").textContent = "Busca las canciones para cargar el álbum";
        document.getElementById("imagenMejorAlbum").src = "https://via.placeholder.com/180?text=Sin+Datos";
    } **/

    
    /**document.getElementById("mejorAlbumArtista").textContent = topAlbum?.nombre || "Sin álbum disponible";
    document.getElementById("imagenMejorAlbum").src = topAlbum?.imagen ?? "https://via.placeholder.com/180?text=Sin+Imagen";
    document.getElementById("imagenMejorAlbum").alt = topAlbum?.nombre ?? "Sin Imagen";**/
}


async function buscarCantante(){
    const nomCantante = document.getElementById("inputArtista").value.trim().replace(/\s+/g, " ");
    const resultado = document.getElementById("resultadoBusqueda");

    if (!nomCantante) {
        resultado.textContent = "Ingrese el nombre de un cantante.";
        return;
    }

    resultado.textContent = "Buscando...";

    try {
        //const response = await fetch(`${API_URL}/artista/buscar/${encodeURIComponent(nomCantante)}`);
        const response = await fetch(`http://localhost:8000/artista/${encodeURIComponent(nomCantante)}`);
        

        const data = await response.json();
        console.log("DATA ARTISTA:", data);

        if (!response.ok || data.error || !data.artista) {
            resultado.textContent = data.error || "Sin coincidencias";
            return;
        }

        console.log("DATA COMPLETA:", data);
        console.log("ARTISTA:", data.artista);
        console.log("SEGUIDORES:", data.metricas?.escuchas);
        console.log("POPULARIDAD:", data.metricas?.popularidad);
        console.log("GENEROS:", data.artista.generos);


        idArtistaActual = data.id_artista;
        

        

        //infoCantante(data.artista);
        infoCantante({
            nombre: data.artista.nombre,
            imagen: data.artista.imagen,
            generos: data.artista.generos,
            seguidores: data.metricas?.escuchas ?? 0,
            popularidad: data.metricas?.popularidad ?? 0,
            mejor_cancion: data.metricas?.cancion_mas_popular ?? "No disponible",
            mejor_album: data.metricas?.album_mas_popular ?? "No disponible",
            imagen_album: data.metricas?.imagen_album_popular ?? ""
        });

        const tbodyCanciones = document.querySelector("#topCancionesArtista tbody");

        if (tbodyCanciones && data.top_canciones) {
            tbodyCanciones.innerHTML = "";
            data.top_canciones.forEach((track, index) => {
                tbodyCanciones.innerHTML += `
                    <tr>
                        <td>${index + 1}</td>
                        <td>${track.nombre}</td>
                        <td>${track.album}</td>
                        <td>${track.popularidad} pts (Spotify)</td>
                    </tr>
                `;
            });
        }

        resultado.textContent = "";

    }     catch (error) {
        console.error(error);
        resultado.textContent = "Ocurrió un error al buscar el cantante.";
    }


}


async function cargarHistoricoArtista() {
    if (!idArtistaActual) {
        alert("Primero busca un artista.");
        return;
    }

    try {
        const response = await fetch(`http://localhost:8000/artista/${idArtistaActual}/historico`);
        const data = await response.json();

        const historico = data.historico || [];

        if (historico.length === 0) {
            alert("No hay histórico para este artista.");
            return;
        }

        const fechas = historico.map(item => item.fecha);
        const vistas = historico.map(item => item.vistas);
        const likes = historico.map(item => item.likes);
        const popularidad = historico.map(item => item.popularidad);

        const ctx = document.getElementById("graficaArtista").getContext("2d");

        if (graficaArtista) {
            graficaArtista.destroy();
        }

        graficaArtista = new Chart(ctx, {
            type: "line",
            data: {
                labels: fechas,
                datasets: [
                    {
                        label: "Vistas YouTube",
                        data: vistas,
                        borderWidth: 2,
                        fill: false
                    },
                    {
                        label: "Likes YouTube",
                        data: likes,
                        borderWidth: 2,
                        fill: false
                    },
                    {
                        label: "Popularidad calculada",
                        data: popularidad,
                        borderWidth: 2,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });

    } catch (error) {
        console.error(error);
        alert("Error al cargar el histórico del artista.");
    }
}




async function exportarAPDF(seccionId) {
    const elemento = document.getElementById(seccionId);
    
    const opt = {
        margin:       0.5,
        filename:     `BeatAndBit_Reporte_${seccionId}.pdf`,
        image:        { type: 'jpeg', quality: 0.98 },
        html2canvas:  { scale: 2, useCORS: true, backgroundColor: "#0b0c10" }, 
        jsPDF:        { unit: 'in', format: 'letter', orientation: 'landscape' }
    };

    await html2pdf().set(opt).from(elemento).save();
}


window.onload = () => {
    mostrarSeccion("inicio");
    cargarTopGlobal();
    cargarPaisesDisponibles();
    cargarTopPaises();
    setInterval(cargarTopGlobal, 60000);

};

document.addEventListener("DOMContentLoaded", () => {
    const btnSincronizar = document.getElementById("btnSincronizar");
    const btnGenerarGrafica = document.getElementById("btnGenerarGrafica");
    
    if(btnSincronizar) {
        btnSincronizar.addEventListener("click", async () => {
            btnSincronizar.disabled = true;
            const textoOriginal = btnSincronizar.innerHTML;
            btnSincronizar.innerHTML = "Sincronizando...";
            btnSincronizar.style.opacity = "0.7";

            try {
                const response = await fetch(`${API_URL}/sincronizar`, {
                    method: 'POST'
                });
                const result = await response.json();

                if (result.status === "success") {
                    alert(result.mensaje); 
                } else if (result.status === "warning") {
                    alert(result.mensaje); 
                } else {
                    alert("Error en el servidor al intentar sincronizar.");
                }
            } catch (error) {
                alert("Error: Sincronización parcial");
            } finally {
                btnSincronizar.innerHTML = textoOriginal;
                btnSincronizar.disabled = false;
                btnSincronizar.style.opacity = "1";
            }
        });
    }

    if (btnGenerarGrafica) {
        btnGenerarGrafica.addEventListener("click", cargarHistorico);
    }

    const btnExportar = document.getElementById("btnExportar");
    const modalExportar = document.getElementById("modalExportar");
    const btnCancelarExportar = document.getElementById("btnCancelarExportar");
    const btnConfirmarExportar = document.getElementById("btnConfirmarExportar");

    if (btnExportar) {
        btnExportar.addEventListener("click", () => {
            modalExportar.style.display = "flex";
        });
    }

    if (btnCancelarExportar) {
        btnCancelarExportar.addEventListener("click", () => {
            modalExportar.style.display = "none";
        });
    }

    if (btnConfirmarExportar) {
        btnConfirmarExportar.addEventListener("click", async () => {
            modalExportar.style.display = "none";

            try {
                const secciones = ["inicio", "paises", "artistas", "historico"];
                let seccionVisibleId = null;
                for (let sec of secciones) {
                    const el = document.getElementById(sec);
                    if (el && el.style.display !== "none") {
                        seccionVisibleId = sec;
                        break;
                    }
                }

                if (!seccionVisibleId) {
                    throw new Error("No se detectó información visible.");
                }

                await exportarAPDF(seccionVisibleId);
            } catch (error) {
                alert("Error al procesar el archivo");
            }
        });
    }
});




