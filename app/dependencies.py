from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient
from typing import Optional
from fastapi import HTTPException

mongo_client: Optional[AsyncIOMotorClient] = None
database_instance: Optional[AsyncIOMotorDatabase] = None

async def get_db() -> AsyncIOMotorDatabase:
    if database_instance is None: raise HTTPException(status_code=503, detail="La base de datos no está disponible.")
    return database_instance