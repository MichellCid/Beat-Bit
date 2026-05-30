import json
import time
import sys
import random
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
from datetime import datetime

sys.stdout.reconfigure(line_buffering=True)

def iniciar_productor():
    intentos = 0
    productor = None
    
    # Intentar conectar durante 60 segundos
    while intentos < 12:
        try:
            print(f"Intentando conectar a Kafka... (Intento {intentos + 1})")
            productor = KafkaProducer(
                bootstrap_servers=['kafka:9092'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            print("¡Conectado a Kafka exitosamente!")
            break
        except NoBrokersAvailable:
            intentos += 1
            time.sleep(5)
    
    if not productor:
        print("No se pudo conectar a Kafka tras varios intentos.")
        return

    artistas = ["The Weeknd", "Taylor Swift", "Bad Bunny", "Dua Lipa"]
    canciones = ["Blinding Lights", "Anti-Hero", "Titi Me Pregunto", "Levitating"]
    paises = ["Mexico", "Estados Unidos", "Espana", "Colombia"]
    
    print("Productor enviando eventos...")
    while True:
        evento = {
            "cancion": random.choice(canciones),
            "artista": random.choice(artistas),
            "pais": random.choice(paises),
            "vistas": random.randint(1, 100),
            "likes": random.randint(0, 10),
            "timestamp": datetime.now().isoformat()
        }
        productor.send('eventos_reproduccion', value=evento)
        productor.flush()
        print(f"Enviado: {evento['cancion']}")
        time.sleep(2)

if __name__ == "__main__":
    time.sleep(15) # Espera inicial para dar tiempo a que arranque Kafka
    iniciar_productor()