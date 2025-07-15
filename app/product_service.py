from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import List, Optional
from common.models import ProductCreate, ProductUpdate, ProductInDB, PyObjectId, RatingCreate, RatingInDB, RatingRead


PRODUCT_COLLECTION = "products"
RATING_COLLECTION = "ratings"

async def get_all_products(
    db: AsyncIOMotorDatabase,
    search: Optional[str] = None,
    category: Optional[str] = None,
    sort_by: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
) -> dict:  # El tipo de retorno ahora es un diccionario
    """
    Obtiene una lista paginada y filtrada de productos, junto con el conteo total.
    """
    query = {}
    if search:
        query["name"] = {"$regex": search, "$options": "i"}
    if category:
        query["category"] = category
        
    # Primero, contamos el total de documentos que coinciden con la consulta
    total_count = await db[PRODUCT_COLLECTION].count_documents(query)
    
    # Luego, aplicamos paginación y ordenamiento para obtener solo la página actual
    products_cursor = db[PRODUCT_COLLECTION].find(query).skip(skip).limit(limit)
    
    if sort_by:
        if sort_by == "price_asc":
            products_cursor = products_cursor.sort("price", 1)
        elif sort_by == "price_desc":
            products_cursor = products_cursor.sort("price", -1)

    product_docs = await products_cursor.to_list(length=limit)
    
    # Devolvemos un diccionario con el total y los productos
    return {
        "total": total_count,
        "products": [ProductInDB(**doc) for doc in product_docs]
    }
async def get_product_by_id(db: AsyncIOMotorDatabase, product_id: str) -> Optional[ProductInDB]:
    if not ObjectId.is_valid(product_id): return None
    doc = await db[PRODUCT_COLLECTION].find_one({"_id": ObjectId(product_id)})
    return ProductInDB(**doc) if doc else None
async def create_product(db: AsyncIOMotorDatabase, product_in: ProductCreate, owner_id: PyObjectId) -> ProductInDB:
    """Crea un nuevo producto en la base de datos, asignando un propietario."""
    product_data = product_in.model_dump()
    product_data["owner_id"] = owner_id # Asigna el propietario
    db_product = ProductInDB(**product_data)
    doc = db_product.model_dump(by_alias=True)
    result = await db[PRODUCT_COLLECTION].insert_one(doc)
    created_doc = await db[PRODUCT_COLLECTION].find_one({"_id": result.inserted_id})
    return ProductInDB(**created_doc)
async def update_product(db: AsyncIOMotorDatabase, product_id: str, product_in: ProductUpdate) -> Optional[ProductInDB]:
    update_data = product_in.model_dump(exclude_unset=True)
    if not update_data: return await get_product_by_id(db, product_id)
    doc = await db[PRODUCT_COLLECTION].find_one_and_update({"_id": ObjectId(product_id)}, {"$set": update_data}, return_document=True)
    return ProductInDB(**doc) if doc else None
async def delete_product(db: AsyncIOMotorDatabase, product_id: str) -> bool:
    result = await db[PRODUCT_COLLECTION].delete_one({"_id": ObjectId(product_id)})
    return result.deleted_count > 0

# Funciones para el sistema de calificaciones
async def create_rating(db: AsyncIOMotorDatabase, rating_in: RatingCreate, user_id: PyObjectId) -> RatingInDB:
    """Crea una nueva calificación para un producto."""
    # Verificar si el usuario ya calificó este producto
    existing_rating = await db[RATING_COLLECTION].find_one({
        "product_id": rating_in.product_id,
        "user_id": user_id
    })
    
    if existing_rating:
        # Actualizar calificación existente
        update_data = rating_in.model_dump(exclude={"product_id"})
        doc = await db[RATING_COLLECTION].find_one_and_update(
            {"_id": existing_rating["_id"]},
            {"$set": update_data},
            return_document=True
        )
        updated_rating = RatingInDB(**doc)
    else:
        # Crear nueva calificación
        rating_data = rating_in.model_dump()
        rating_data["user_id"] = user_id
        db_rating = RatingInDB(**rating_data)
        doc = db_rating.model_dump(by_alias=True)
        result = await db[RATING_COLLECTION].insert_one(doc)
        created_doc = await db[RATING_COLLECTION].find_one({"_id": result.inserted_id})
        updated_rating = RatingInDB(**created_doc)
    
    # Actualizar el promedio de calificaciones del producto
    await update_product_rating_average(db, rating_in.product_id)
    
    return updated_rating

async def get_product_ratings(db: AsyncIOMotorDatabase, product_id: str) -> List[RatingRead]:
    """Obtiene todas las calificaciones de un producto."""
    if not ObjectId.is_valid(product_id):
        return []
    
    ratings_cursor = db[RATING_COLLECTION].find({"product_id": ObjectId(product_id)})
    rating_docs = await ratings_cursor.to_list(length=None)
    return [RatingRead(**doc) for doc in rating_docs]

async def update_product_rating_average(db: AsyncIOMotorDatabase, product_id: PyObjectId):
    """Actualiza el promedio de calificaciones de un producto."""
    pipeline = [
        {"$match": {"product_id": product_id}},
        {"$group": {
            "_id": "$product_id",
            "average_rating": {"$avg": "$rating"},
            "total_ratings": {"$sum": 1}
        }}
    ]
    
    result = await db[RATING_COLLECTION].aggregate(pipeline).to_list(length=1)
    
    if result:
        avg_rating = round(result[0]["average_rating"], 2)
        total_ratings = result[0]["total_ratings"]
    else:
        avg_rating = 0.0
        total_ratings = 0
    
    # Actualizar el producto con el nuevo promedio
    await db[PRODUCT_COLLECTION].update_one(
        {"_id": product_id},
        {"$set": {
            "average_rating": avg_rating,
            "total_ratings": total_ratings
        }}
    )

async def get_user_rating_for_product(db: AsyncIOMotorDatabase, product_id: str, user_id: PyObjectId) -> Optional[RatingRead]:
    """Obtiene la calificación de un usuario específico para un producto."""
    if not ObjectId.is_valid(product_id):
        return None
    
    doc = await db[RATING_COLLECTION].find_one({
        "product_id": ObjectId(product_id),
        "user_id": user_id
    })
    
    return RatingRead(**doc) if doc else None