const API_URL = "http://localhost:8000/api";

function mostrarSeccion(id) {
    document.querySelectorAll("#inicio, #paises, #artistas").forEach(sec => {
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
        console.error("Error cargando países:", error);
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
        console.error("Error cargando ciudades:", error);
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
        console.error("Error cargando top por países:", error);
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
        console.error("Error cargando top por ciudad:", error);
        mostrarMensajeCiudad("No hay rankings disponibles para esta ciudad");
    }
}

window.onload = () => {
    mostrarSeccion("inicio");
    cargarTopGlobal();
    cargarPaisesDisponibles();
    cargarTopPaises();
    setInterval(cargarTopGlobal, 60000);
};