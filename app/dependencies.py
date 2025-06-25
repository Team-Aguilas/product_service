# products_service/app/dependencies.py (VERSIÓN FINAL Y CORREGIDA)

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient
from bson import ObjectId
from typing import Optional

from .config import settings
from common.models import UserInDB  # Importa el modelo de usuario desde common
from .security import decode_access_token # Importa la función de seguridad local

# Variables globales para la conexión (manejadas por el lifespan en main.py)
mongo_client: Optional[AsyncIOMotorClient] = None
database_instance: Optional[AsyncIOMotorDatabase] = None

async def get_db() -> AsyncIOMotorDatabase:
    """Dependencia para obtener la sesión de la base de datos."""
    if database_instance is None:
        raise HTTPException(status_code=503, detail="La base de datos no está disponible.")
    return database_instance

# --- Lógica de DB para buscar usuarios (local a este servicio) ---
async def _get_user_by_id_from_db(db: AsyncIOMotorDatabase, user_id: str) -> Optional[UserInDB]:
    """Función interna para obtener un usuario por ID desde la DB."""
    if not ObjectId.is_valid(user_id):
        return None
    user_doc = await db["users"].find_one({"_id": ObjectId(user_id)})
    if user_doc:
        return UserInDB(**user_doc)
    return None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(db: AsyncIOMotorDatabase = Depends(get_db), token: str = Depends(oauth2_scheme)) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None or payload.get("sub") is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    
    # Usa la función local en lugar de importar user_service
    user = await _get_user_by_id_from_db(db, user_id=user_id)
    
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario inactivo")
    return current_user

async def get_current_active_superuser(current_user: UserInDB = Depends(get_current_active_user)) -> UserInDB:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario no tiene suficientes privilegios",
        )
    return current_user