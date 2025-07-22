"""
Script para migrar productos existentes y agregar campos de calificación
Ejecutar una sola vez después de implementar el sistema de calificaciones
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

# Configuración de la base de datos
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "products_db")

async def migrate_products():
    """Migra todos los productos existentes para agregar campos de calificación"""
    
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    
    try:
        # Actualizar todos los productos que no tienen los campos de calificación
        result = await db.products.update_many(
            {
                "$or": [
                    {"average_rating": {"$exists": False}},
                    {"total_ratings": {"$exists": False}}
                ]
            },
            {
                "$set": {
                    "average_rating": 0.0,
                    "total_ratings": 0
                }
            }
        )
        
        print(f"Productos actualizados: {result.modified_count}")
        
        # Verificar el resultado
        products_count = await db.products.count_documents({})
        products_with_rating = await db.products.count_documents({
            "average_rating": {"$exists": True},
            "total_ratings": {"$exists": True}
        })
        
        print(f"Total de productos: {products_count}")
        print(f"Productos con campos de calificación: {products_with_rating}")
        
        if products_count == products_with_rating:
            print("✅ Migración completada exitosamente")
        else:
            print("⚠️ Algunos productos podrían no haberse migrado correctamente")
            
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    print("Iniciando migración de productos...")
    asyncio.run(migrate_products())
