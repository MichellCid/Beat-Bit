from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.dashboard import router as dashboard_router
from servicios.sincronizacion import sincronizar_datos
from servicios.transformaciones import crear_esquema_data_warehouse

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

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
    resultado_transformacion = crear_esquema_data_warehouse()
    return {
        "extraccion": resultado_extraccion,
        "transformacion": resultado_transformacion
    }