const API_URL = "http://localhost:8000/api";

let chartInstance = null;
let idArtistaActual = null;
let graficaArtista = null;
let comparacionActiva = false;

function mostrarSeccion(id) {
    document.querySelectorAll("#inicio, #paises, #artistas, #historico, #demografia").forEach(sec => {
        sec.style.display = "none";
    });

    const seccion = document.getElementById(id);
    if (seccion) {
        seccion.style.display = "block";
    }
}

/* =========================================================
   INICIO / TOP GLOBAL
========================================================= */

async function cargarTopGlobal() {
    const errorMsg = document.getElementById("errorMensajeGlobal");

    if (errorMsg) {
        errorMsg.style.display = "none";
        errorMsg.textContent = "";
    }

    try {
        const response = await fetch(`${API_URL}/top-global`);

        if (!response.ok) {
            throw new Error("Falla en el servidor");
        }

        const data = await response.json();

        localStorage.setItem("cache_top_global", JSON.stringify(data));
        renderizarDashboardGlobal(data);

    } catch (error) {
        console.error("Error cargando top global:", error);

        if (errorMsg) {
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
    const pistas = (data.top_global || []).sort((a, b) => {
        return Number(b.reproducciones) - Number(a.reproducciones);
    });

    if (data.artista_top) {
        const artistaNum1 = document.getElementById("artistaNum1");
        const imagen = document.getElementById("imagenArtistaNum1");

        if (artistaNum1) {
            artistaNum1.textContent = data.artista_top.nombre;
        }

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

        const cancionNum1 = document.getElementById("cancionNum1");
        const artistaCancionNum1 = document.getElementById("artistaCancionNum1");
        const albumNum1 = document.getElementById("albumNum1");

        if (cancionNum1) {
            cancionNum1.textContent = topTrack.nombre_cancion;
        }

        if (artistaCancionNum1) {
            artistaCancionNum1.textContent = topTrack.nombre_artista;
        }

        if (albumNum1) {
            albumNum1.textContent = `${topTrack.nombre_cancion} - Single`;
        }
    }

    const leaderboard = document.getElementById("leaderboardTopMundial");

    if (leaderboard) {
        leaderboard.innerHTML = "";

        pistas.slice(0, 10).forEach((track, index) => {
            const rank = index + 1;
            const rankStr = rank < 10 ? `0${rank}` : rank;
            const rankClass = rank <= 3 ? `top-${rank}` : "";
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

/* =========================================================
   MENSAJES
========================================================= */

function mostrarMensajePais(text, ubicacion = "A") {
    const id = ubicacion === "B" ? "mensajePaisB" : "mensajePais";
    const mensaje = document.getElementById(id);

    if (mensaje) {
        mensaje.textContent = text || "";
    }
}

function mostrarMensajeCiudad(text, ubicacion = "A") {
    const id = ubicacion === "B" ? "mensajeCiudadB" : "mensajeCiudad";
    const mensaje = document.getElementById(id);

    if (mensaje) {
        mensaje.textContent = text || "";
    }
}

/* =========================================================
   PAÍSES A Y B
========================================================= */

async function cargarPaisesDisponibles() {
    try {
        const response = await fetch(`${API_URL}/paises`);

        if (!response.ok) {
            throw new Error("Error al cargar países");
        }

        const data = await response.json();

        const selectA = document.getElementById("selectPais");
        const selectB = document.getElementById("selectPaisB");

        if (!data.paises || data.paises.length === 0) {
            console.warn("La API no devolvió países");
            return;
        }

        function llenarSelect(select) {
            if (!select) return;

            select.innerHTML = `<option value="">Todos los países</option>`;

            data.paises.forEach(pais => {
                const option = document.createElement("option");
                option.value = pais;
                option.textContent = pais;
                select.appendChild(option);
            });
        }

        llenarSelect(selectA);
        llenarSelect(selectB);

        if (selectA) {
            selectA.addEventListener("change", () => {
                cargarTopPaises(selectA.value, "A");
                cargarCiudadesDisponible(selectA.value, "A");
            });
        }

        if (selectB) {
            selectB.addEventListener("change", () => {
                cargarTopPaises(selectB.value, "B");
                cargarCiudadesDisponible(selectB.value, "B");
            });
        }

        const btnLimpiarA = document.getElementById("btnLimpiarPais");
        if (btnLimpiarA && selectA) {
            btnLimpiarA.addEventListener("click", () => {
                selectA.value = "";
                cargarTopPaises("", "A");
                ocultarCiudades("A");
            });
        }

        const btnLimpiarB = document.getElementById("btnLimpiarPaisB");
        if (btnLimpiarB && selectB) {
            btnLimpiarB.addEventListener("click", () => {
                selectB.value = "";
                cargarTopPaises("", "B");
                ocultarCiudades("B");
            });
        }

    } catch (error) {
        console.error("Error cargando países:", error);
    }
}

/* =========================================================
   CIUDADES A Y B
========================================================= */

function ocultarCiudades(ubicacion = "A") {
    const sectionId = ubicacion === "B" ? "ciudadSectionB" : "ciudadSection";
    const selectId = ubicacion === "B" ? "selectCiudadB" : "selectCiudad";
    const inputId = ubicacion === "B" ? "inputCiudadB" : "inputCiudad";
    const dataListId = ubicacion === "B" ? "ciudadesDatalistB" : "ciudadesDatalist";
    const tablaId = ubicacion === "B" ? "#tablaTopCiudadB tbody" : "#tablaTopCiudad tbody";

    const section = document.getElementById(sectionId);
    const select = document.getElementById(selectId);
    const input = document.getElementById(inputId);
    const dataList = document.getElementById(dataListId);
    const tbody = document.querySelector(tablaId);

    if (section) {
        section.style.display = "none";
    }

    if (select) {
        select.innerHTML = `<option value="">Elige una ciudad</option>`;
    }

    if (input) {
        input.value = "";
    }

    if (dataList) {
        dataList.innerHTML = "";
    }

    if (tbody) {
        tbody.innerHTML = "";
    }

    mostrarMensajeCiudad("", ubicacion);
}

async function cargarCiudadesDisponible(pais, ubicacion = "A") {
    if (!pais) {
        ocultarCiudades(ubicacion);
        return;
    }

    try {
        const response = await fetch(`${API_URL}/ciudades?country=${encodeURIComponent(pais)}`);
        const data = await response.json();

        const sectionId = ubicacion === "B" ? "ciudadSectionB" : "ciudadSection";
        const selectId = ubicacion === "B" ? "selectCiudadB" : "selectCiudad";
        const inputId = ubicacion === "B" ? "inputCiudadB" : "inputCiudad";
        const dataListId = ubicacion === "B" ? "ciudadesDatalistB" : "ciudadesDatalist";
        const btnLimpiarId = ubicacion === "B" ? "btnLimpiarCiudadB" : "btnLimpiarCiudad";
        const btnBuscarId = ubicacion === "B" ? "btnBuscarCiudadB" : "btnBuscarCiudad";
        const selectPaisId = ubicacion === "B" ? "selectPaisB" : "selectPais";

        const section = document.getElementById(sectionId);
        const select = document.getElementById(selectId);
        const dataList = document.getElementById(dataListId);
        const input = document.getElementById(inputId);

        if (!section || !select || !dataList || !input) {
            console.warn(`Faltan elementos HTML para ciudad en ubicación ${ubicacion}`);
            return;
        }

        const cities = data.ciudades || [];

        if (!cities.length) {
            ocultarCiudades(ubicacion);
            mostrarMensajeCiudad("No hay ciudades disponibles para este país.", ubicacion);
            return;
        }

        section.style.display = "block";
        select.innerHTML = `<option value="">Elige una ciudad</option>`;
        dataList.innerHTML = "";
        input.value = "";
        mostrarMensajeCiudad("", ubicacion);

        cities.forEach(ciudad => {
            select.innerHTML += `<option value="${ciudad}">${ciudad}</option>`;
            dataList.innerHTML += `<option value="${ciudad}"></option>`;
        });

        select.onchange = () => {
            if (select.value) {
                input.value = select.value;

                const paisSeleccionado = document.getElementById(selectPaisId).value;
                cargarTopCiudad(paisSeleccionado, select.value, ubicacion);
            }
        };

        const btnLimpiarCiudad = document.getElementById(btnLimpiarId);
        if (btnLimpiarCiudad) {
            btnLimpiarCiudad.onclick = () => {
                select.value = "";
                input.value = "";

                const tbodyId = ubicacion === "B" ? "#tablaTopCiudadB tbody" : "#tablaTopCiudad tbody";
                const tbody = document.querySelector(tbodyId);

                if (tbody) {
                    tbody.innerHTML = "";
                }

                mostrarMensajeCiudad("", ubicacion);
            };
        }

        const btnBuscarCiudad = document.getElementById(btnBuscarId);
        if (btnBuscarCiudad) {
            btnBuscarCiudad.onclick = () => {
                const selectedCiudad = select.value.trim();
                const typedCiudad = input.value.trim();
                const ciudad = typedCiudad || selectedCiudad;

                if (ciudad) {
                    const paisSeleccionado = document.getElementById(selectPaisId).value;

                    cargarTopCiudad(paisSeleccionado, ciudad, ubicacion);
                    select.value = ciudad;
                    input.value = ciudad;
                }
            };
        }

    } catch (error) {
        console.error(`Error cargando ciudades para ubicación ${ubicacion}:`, error);
        mostrarMensajeCiudad("Ocurrió un error al cargar las ciudades.", ubicacion);
    }
}

/* =========================================================
   TOP POR PAÍS A Y B
========================================================= */

async function cargarTopPaises(pais = "", ubicacion = "A") {
    try {
        mostrarMensajePais("", ubicacion);
        mostrarMensajeCiudad("", ubicacion);

        const url = pais
            ? `${API_URL}/top-paises?country=${encodeURIComponent(pais)}`
            : `${API_URL}/top-paises`;

        const response = await fetch(url);
        const data = await response.json();

        const tablaId = ubicacion === "B" ? "#tablaTopPaisesB tbody" : "#tablaTopPaises tbody";
        const tbody = document.querySelector(tablaId);

        if (!tbody) return;

        tbody.innerHTML = "";

        if (!data.top_paises || data.top_paises.length === 0) {
            if (pais) {
                mostrarMensajePais("Sin datos registrados para esta región.", ubicacion);
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
        console.error(`Error cargando top países ${ubicacion}:`, error);
        mostrarMensajePais("Ocurrió un error al cargar los datos del país.", ubicacion);
    }
}

/* =========================================================
   TOP POR CIUDAD A Y B
========================================================= */

async function cargarTopCiudad(pais, ciudad, ubicacion = "A") {
    if (!pais || !ciudad) {
        mostrarMensajeCiudad("Selecciona un país y una ciudad para ver el ranking local.", ubicacion);
        return;
    }

    try {
        mostrarMensajeCiudad("", ubicacion);

        const response = await fetch(`${API_URL}/top-ciudad?country=${encodeURIComponent(pais)}&city=${encodeURIComponent(ciudad)}`);
        const data = await response.json();

        const tablaId = ubicacion === "B" ? "#tablaTopCiudadB tbody" : "#tablaTopCiudad tbody";
        const tbody = document.querySelector(tablaId);

        if (!tbody) return;

        tbody.innerHTML = "";

        if (!data.top_ciudad || data.top_ciudad.length === 0) {
            mostrarMensajeCiudad("No hay rankings disponibles para esta ciudad.", ubicacion);
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
        console.error(`Error cargando top ciudad ${ubicacion}:`, error);
        mostrarMensajeCiudad("No hay rankings disponibles para esta ciudad.", ubicacion);
    }
}

/* =========================================================
   HISTÓRICO
========================================================= */

async function cargarHistorico() {
    const inputInicio = document.getElementById("anioInicio").value;
    const inputFin = document.getElementById("anioFin").value;
    const mensajeError = document.getElementById("mensajeHistorico");

    if (mensajeError) {
        mensajeError.style.display = "none";
    }

    let anioFin = inputFin ? parseInt(inputFin) : new Date().getFullYear();
    let anioInicio = inputInicio ? parseInt(inputInicio) : anioFin - 5;

    try {
        const response = await fetch(`${API_URL}/historico?inicio=${anioInicio}&fin=${anioFin}`);
        const data = await response.json();

        if (!data.evolucion || data.evolucion.length === 0) {
            if (mensajeError) {
                mensajeError.textContent = "Error: No hay datos para el periodo";
                mensajeError.style.display = "block";
            }

            if (chartInstance) {
                chartInstance.destroy();
            }

            return;
        }

        renderizarGraficaHistorico(data.evolucion);

    } catch (error) {
        if (mensajeError) {
            mensajeError.textContent = "Error al conectar con el servidor.";
            mensajeError.style.display = "block";
        }
    }
}

function renderizarGraficaHistorico(datos) {
    const canvas = document.getElementById("graficaHistorico");

    if (!canvas) return;

    const ctx = canvas.getContext("2d");

    if (chartInstance) {
        chartInstance.destroy();
    }

    const etiquetasAnios = datos.map(d => d.anio);
    const generos = Object.keys(datos[0]).filter(key => key !== "anio");
    const colores = ["#3498db", "#e74c3c", "#2ecc71", "#f1c40f", "#9b59b6"];

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
        type: "line",
        data: {
            labels: etiquetasAnios,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: "#ffffff"
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: "#aaaaaa"
                    },
                    grid: {
                        color: "#333333"
                    }
                },
                y: {
                    ticks: {
                        color: "#aaaaaa"
                    },
                    grid: {
                        color: "#333333"
                    }
                }
            }
        }
    });
}

/* =========================================================
   ARTISTAS
========================================================= */

async function infoCantante(artista, topAlbum = null) {
    document.getElementById("nombrePerfilArtista").textContent = artista.nombre;
    document.getElementById("imagenPerfilArtista").src = artista.imagen || "https://via.placeholder.com/180?text=Sin+Imagen";
    document.getElementById("imagenPerfilArtista").alt = artista.nombre || "Sin Imagen";

    document.getElementById("seguidoresArtista").textContent = Number(artista.seguidores ?? 0).toLocaleString();
    document.getElementById("popularidadArtista").textContent = artista.popularidad ?? "0";

    document.getElementById("generosArtista").textContent =
        artista.generos && artista.generos.length > 0
            ? artista.generos.join(", ")
            : "No especificados";

    if (topAlbum) {
        document.getElementById("mejorAlbumArtista").textContent = topAlbum.nombre || "No disponible";
        document.getElementById("imagenMejorAlbum").src = topAlbum.imagen ?? "https://via.placeholder.com/180?text=Sin+Imagen";
        document.getElementById("imagenMejorAlbum").alt = topAlbum.nombre ?? "Sin Imagen";
    } else {
        document.getElementById("mejorAlbumArtista").textContent = "Busca las canciones para cargar el álbum";
        document.getElementById("imagenMejorAlbum").src = "https://via.placeholder.com/180?text=Sin+Datos";
    }
}

async function buscarCantante() {
    const nomCantante = document.getElementById("inputArtista").value.trim().replace(/\s+/g, " ");
    const resultado = document.getElementById("resultadoBusqueda");

    if (!nomCantante) {
        resultado.textContent = "Ingrese el nombre de un cantante.";
        return;
    }

    resultado.textContent = "Buscando...";

    try {
        const response = await fetch(`http://localhost:8000/artista/${encodeURIComponent(nomCantante)}`);
        const data = await response.json();

        console.log("DATA ARTISTA:", data);

        if (!response.ok || data.error || !data.artista) {
            resultado.textContent = data.error || "Sin coincidencias";
            return;
        }

        idArtistaActual = data.id_artista;

        infoCantante({
            nombre: data.artista.nombre,
            imagen: data.artista.imagen,
            generos: data.artista.generos,
            seguidores: data.metricas?.escuchas ?? 0,
            popularidad: data.metricas?.popularidad ?? 0
        });

        resultado.textContent = "";

    } catch (error) {
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

/* =========================================================
   EXPORTAR PDF
========================================================= */

async function exportarAPDF(seccionId) {
    const elemento = document.getElementById(seccionId);

    const opt = {
        margin: 0.5,
        filename: `BeatAndBit_Reporte_${seccionId}.pdf`,
        image: {
            type: "jpeg",
            quality: 0.98
        },
        html2canvas: {
            scale: 2,
            useCORS: true,
            backgroundColor: "#0b0c10"
        },
        jsPDF: {
            unit: "in",
            format: "letter",
            orientation: "landscape"
        }
    };

    await html2pdf().set(opt).from(elemento).save();
}

/* =========================================================
   DEMOGRAFÍA
========================================================= */

let datosOyentes = [];
let ordenDescendente = true;

async function cargarTopOyentes() {
    const btn = document.getElementById("btnTopOyentes");
    const mensaje = document.getElementById("mensajeDemografia");
    const tabla = document.getElementById("tablaTopOyentes");

    if (btn) {
        btn.disabled = true;
        btn.textContent = "Cargando...";
    }

    if (mensaje) {
        mensaje.style.display = "none";
    }

    try {
        const response = await fetch(`${API_URL}/top-audiencia-regiones`);

        if (!response.ok) {
            throw new Error("Error en la API");
        }

        const data = await response.json();

        datosOyentes = data.top_audiencia || [];
        ordenDescendente = true;

        const colOyentes = document.getElementById("colOyentes");

        if (colOyentes) {
            colOyentes.textContent = "Oyentes Totales ⬇";
        }

        renderizarTablaOyentes();

        if (tabla) {
            tabla.style.display = "table";
        }

    } catch (error) {
        if (mensaje) {
            mensaje.textContent = "Error de carga de audiencia. No se pudo obtener la información.";
            mensaje.style.display = "block";
        }
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.textContent = "Top Oyentes por Región";
        }
    }
}

function renderizarTablaOyentes() {
    const tbody = document.querySelector("#tablaTopOyentes tbody");

    if (!tbody) return;

    tbody.innerHTML = "";

    const datosOrdenados = [...datosOyentes].sort((a, b) => {
        const valA = a.oyentes === "N/A" ? -1 : a.oyentes;
        const valB = b.oyentes === "N/A" ? -1 : b.oyentes;

        if (ordenDescendente) {
            return valB - valA;
        } else {
            return valA - valB;
        }
    });

    datosOrdenados.forEach((item, index) => {
        const oyentesDisplay = item.oyentes === "N/A"
            ? "N/A"
            : Number(item.oyentes).toLocaleString();

        tbody.innerHTML += `
            <tr>
                <td>${index + 1}</td>
                <td>${item.region}</td>
                <td>${oyentesDisplay}</td>
            </tr>
        `;
    });
}

function invertirOrdenOyentes() {
    ordenDescendente = !ordenDescendente;

    const colOyentes = document.getElementById("colOyentes");

    if (colOyentes) {
        colOyentes.textContent = ordenDescendente
            ? "Oyentes Totales ⬇"
            : "Oyentes Totales ⬆";
    }

    renderizarTablaOyentes();
}

/* =========================================================
   EVENTOS INICIALES
========================================================= */

window.onload = () => {
    mostrarSeccion("inicio");
    cargarTopGlobal();
    cargarPaisesDisponibles();
    cargarTopPaises("", "A");

    setInterval(cargarTopGlobal, 60000);
};

document.addEventListener("DOMContentLoaded", () => {
    const btnSincronizar = document.getElementById("btnSincronizar");
    const btnGenerarGrafica = document.getElementById("btnGenerarGrafica");
    const btnComparar = document.getElementById("btnComparar");

    if (btnComparar) {
        btnComparar.addEventListener("click", () => {
            comparacionActiva = !comparacionActiva;

            const panelB = document.getElementById("panelB");

            if (!panelB) return;

            if (comparacionActiva) {
                panelB.style.display = "block";
                btnComparar.textContent = "Cerrar Comparación";

                const selectPaisB = document.getElementById("selectPaisB");

                if (selectPaisB && selectPaisB.value) {
                    cargarTopPaises(selectPaisB.value, "B");
                    cargarCiudadesDisponible(selectPaisB.value, "B");
                }

            } else {
                panelB.style.display = "none";
                btnComparar.textContent = "Comparar Ubicaciones";
            }
        });
    }

    if (btnSincronizar) {
        btnSincronizar.addEventListener("click", async () => {
            btnSincronizar.disabled = true;

            const textoOriginal = btnSincronizar.innerHTML;

            btnSincronizar.innerHTML = "Sincronizando...";
            btnSincronizar.style.opacity = "0.7";

            try {
                const response = await fetch(`${API_URL}/sincronizar`, {
                    method: "POST"
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
            if (modalExportar) {
                modalExportar.style.display = "flex";
            }
        });
    }

    if (btnCancelarExportar) {
        btnCancelarExportar.addEventListener("click", () => {
            if (modalExportar) {
                modalExportar.style.display = "none";
            }
        });
    }

    if (btnConfirmarExportar) {
        btnConfirmarExportar.addEventListener("click", async () => {
            if (modalExportar) {
                modalExportar.style.display = "none";
            }

            try {
                const secciones = ["inicio", "paises", "artistas", "historico", "demografia"];
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

    const btnTopOyentes = document.getElementById("btnTopOyentes");

    if (btnTopOyentes) {
        btnTopOyentes.addEventListener("click", cargarTopOyentes);
    }

    const colOyentes = document.getElementById("colOyentes");

    if (colOyentes) {
        colOyentes.addEventListener("click", invertirOrdenOyentes);
    }
});