from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import List, Optional
from common.models import ProductCreate, ProductUpdate, ProductInDB, PyObjectId


PRODUCT_COLLECTION = "products"

async def get_all_products(
    db: AsyncIOMotorDatabase,
    search: Optional[str] = None,
    category: Optional[str] = None,
    sort_by: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
) -> List[ProductInDB]:
    """
    Obtiene una lista de todos los productos con filtros y ordenamiento opcionales.
    """
    query = {}
    
    # 1. Filtro de Búsqueda por nombre (insensible a mayúsculas/minúsculas)
    if search:
        query["name"] = {"$regex": search, "$options": "i"}
        
    # 2. Filtro por Categoría
    if category:
        query["category"] = category
        
    # Construye el cursor de la base de datos con los filtros
    products_cursor = db[PRODUCT_COLLECTION].find(query).skip(skip).limit(limit)
    
    # 3. Ordenamiento
    if sort_by:
        if sort_by == "price_asc":
            products_cursor = products_cursor.sort("price", 1)
        elif sort_by == "price_desc":
            products_cursor = products_cursor.sort("price", -1)

    product_docs = await products_cursor.to_list(length=limit)
    return [ProductInDB(**doc) for doc in product_docs]
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