from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from routes.dashboard import router as dashboard_router
from servicios.sincronizacion import sincronizar_datos
from servicios.transformaciones import estandarizar_metricas_popularidad

def tarea_sincronizacion_automatica():
    sincronizar_datos()
    estandarizar_metricas_popularidad()

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = BackgroundScheduler()
    scheduler.add_job(tarea_sincronizacion_automatica, 'interval', minutes=1) 
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(title="Beat & Bit API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard_router, prefix="/api")

@app.get("/")
def home():
    return {"message": "API funcionando"}

@app.post("/api/sincronizar")
def endpoint_sincronizar():
    resultado_extraccion = sincronizar_datos()
    resultado_transformacion = estandarizar_metricas_popularidad()
    
    return {
        "extraccion": resultado_extraccion,
        "transformacion": resultado_transformacion
    }