def calcular_popularidad(escuchas, reproducciones, vistas, likes):
    puntuacion = (
        escuchas * 0.25 +
        reproducciones * 0.25 +
        vistas * 0.35 +
        likes * 0.15
    )

    popularidad = puntuacion / 1_000_000

    return round(min(popularidad, 100), 2)
