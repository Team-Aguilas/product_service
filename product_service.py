# app/services/product_service.py
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import List, Optional

from app.models import ProductCreate, ProductUpdate, ProductInDB

PRODUCT_COLLECTION = "products"

async def get_all_products(db: AsyncIOMotorDatabase, skip: int = 0, limit: int = 20) -> List[ProductInDB]:
    """Obtiene una lista de todos los productos."""
    products_cursor = db[PRODUCT_COLLECTION].find().skip(skip).limit(limit)
    product_docs = await products_cursor.to_list(length=limit)
    return [ProductInDB(**doc) for doc in product_docs]

async def get_product_by_id(db: AsyncIOMotorDatabase, product_id: str) -> Optional[ProductInDB]:
    """Obtiene un producto por su ID."""
    if not ObjectId.is_valid(product_id):
        return None
    product_doc = await db[PRODUCT_COLLECTION].find_one({"_id": ObjectId(product_id)})
    if product_doc:
        return ProductInDB(**product_doc)
    return None

async def create_product(db: AsyncIOMotorDatabase, product_in: ProductCreate) -> ProductInDB:
    """Crea un nuevo producto en la base de datos."""
    db_product = ProductInDB(**product_in.model_dump())
    product_doc_to_insert = db_product.model_dump(by_alias=True, exclude_none=True)
    
    result = await db[PRODUCT_COLLECTION].insert_one(product_doc_to_insert)
    created_doc = await db[PRODUCT_COLLECTION].find_one({"_id": result.inserted_id})
    if created_doc:
        return ProductInDB(**created_doc)
    # Este caso es improbable si la inserción fue exitosa
    raise Exception("No se pudo crear el producto después de la inserción.")

async def update_product(db: AsyncIOMotorDatabase, product_id: str, product_in: ProductUpdate) -> Optional[ProductInDB]:
    """Actualiza un producto existente."""
    update_data = product_in.model_dump(exclude_unset=True)
    if not update_data:
        # Si no hay datos, no hay nada que actualizar. Se podría devolver el producto existente.
        return await get_product_by_id(db, product_id)

    updated_doc = await db[PRODUCT_COLLECTION].find_one_and_update(
        {"_id": ObjectId(product_id)},
        {"$set": update_data},
        return_document=True
    )
    if updated_doc:
        return ProductInDB(**updated_doc)
    return None

async def delete_product(db: AsyncIOMotorDatabase, product_id: str) -> bool:
    """Elimina un producto por su ID."""
    delete_result = await db[PRODUCT_COLLECTION].delete_one({"_id": ObjectId(product_id)})
    return delete_result.deleted_count > 0