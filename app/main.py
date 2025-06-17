from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from . import dependencies as global_deps, config
from .product_router import router as product_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    global_deps.mongo_client = AsyncIOMotorClient(config.settings.MONGO_URI)
    global_deps.database_instance = global_deps.mongo_client[config.settings.MONGO_DB_NAME]
    print(f"Servicio '{config.settings.PROJECT_NAME}' conectado a MongoDB.")
    yield
    global_deps.mongo_client.close()
    print(f"Servicio '{config.settings.PROJECT_NAME}' desconectado.")

app = FastAPI(title=config.settings.PROJECT_NAME, lifespan=lifespan)
app.mount("/static", StaticFiles(directory="products_service/static"), name="static")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(product_router, prefix="/api/v1/products", tags=["Products"])

@app.get("/")
def read_root(): return {"service": config.settings.PROJECT_NAME, "status": "ok"}