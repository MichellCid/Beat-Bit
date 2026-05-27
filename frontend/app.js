const API_URL = "http://localhost:8000/api";

function mostrarSeccion(id) {
    document.querySelectorAll("#inicio, #paises, #artistas").forEach(sec => {
        sec.style.display = "none";
    });

    document.getElementById(id).style.display = "block";
}

async function cargarTopGlobal() {
    try {
        const response = await fetch(`${API_URL}/top-global`);
        const data = await response.json();

        document.getElementById("artistaNum1").textContent =
            data.artista_top.nombre;

        const imagen = document.getElementById("imagenArtistaNum1");

        if (imagen) {
            imagen.src = data.artista_top.imagen;
            imagen.alt = data.artista_top.nombre;
        }

        const tbody = document.querySelector("#tablaTopMundial tbody");
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

    } catch (error) {
        console.error("Error cargando top global:", error);
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
        });

        const btnLimpiar = document.getElementById("btnLimpiarPais");
        if (btnLimpiar) {
            btnLimpiar.addEventListener("click", () => {
                select.value = "";
                cargarTopPaises();
            });
        }
    } catch (error) {
        console.error("Error cargando países:", error);
    }
}

async function cargarTopPaises(pais = "") {
    try {
        mostrarMensajePais("");
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

window.onload = () => {
    mostrarSeccion("inicio");
    cargarTopGlobal();
    cargarPaisesDisponibles();
    cargarTopPaises();
    setInterval(cargarTopGlobal, 60000);
};