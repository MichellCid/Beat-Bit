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

window.onload = () => {
    mostrarSeccion("inicio");
    cargarTopGlobal();
    setInterval(cargarTopGlobal, 60000);
};