from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import List, Optional
from common.models import ProductCreate, ProductUpdate, ProductInDB

PRODUCT_COLLECTION = "products"

async def get_all_products(db: AsyncIOMotorDatabase, skip: int = 0, limit: int = 20) -> List[ProductInDB]:
    docs = await db[PRODUCT_COLLECTION].find().skip(skip).limit(limit).to_list(length=limit)
    return [ProductInDB(**doc) for doc in docs]
async def get_product_by_id(db: AsyncIOMotorDatabase, product_id: str) -> Optional[ProductInDB]:
    if not ObjectId.is_valid(product_id): return None
    doc = await db[PRODUCT_COLLECTION].find_one({"_id": ObjectId(product_id)})
    return ProductInDB(**doc) if doc else None
async def create_product(db: AsyncIOMotorDatabase, product_in: ProductCreate) -> ProductInDB:
    db_product = ProductInDB(**product_in.model_dump())
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