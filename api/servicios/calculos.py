#def calcular_popularidad(escuchas, reproducciones, vistas, likes):
 #   puntuacion = (
  #      escuchas * 0.25 +
   #     reproducciones * 0.25 +
    #    vistas * 0.35 +
     #   likes * 0.15
    #)

 #   popularidad = puntuacion / 1_000_000

#    return round(min(popularidad, 100), 2)


import math

def calcular_popularidad(escuchas, reproducciones, vistas, likes):
    escuchas = max(0, escuchas or 0)
    reproducciones = max(0, reproducciones or 0)
    vistas = max(0, vistas or 0)
    likes = max(0, likes or 0)

    score = (
        math.log10(escuchas + 1) * 20 +
        math.log10(reproducciones + 1) * 25 +
        math.log10(vistas + 1) * 30 +
        math.log10(likes + 1) * 25
    )

    popularidad = min(100, round(score / 4, 2))

    return popularidad