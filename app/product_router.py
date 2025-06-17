from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
from .dependencies import get_db
from common.models import ProductCreate, ProductRead, ProductUpdate
from . import product_service

router = APIRouter()

@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_new_product(product_in: ProductCreate, db: AsyncIOMotorDatabase = Depends(get_db)):
    return await product_service.create_product(db, product_in=product_in)
@router.get("/", response_model=List[ProductRead])
async def read_all_products(skip: int = 0, limit: int = 20, db: AsyncIOMotorDatabase = Depends(get_db)):
    return await product_service.get_all_products(db, skip=skip, limit=limit)
@router.get("/{product_id}", response_model=ProductRead)
async def read_product_by_id(product_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    product = await product_service.get_product_by_id(db, product_id=product_id)
    if not product: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return product
@router.put("/{product_id}", response_model=ProductRead)
async def update_existing_product(product_id: str, product_in: ProductUpdate, db: AsyncIOMotorDatabase = Depends(get_db)):
    if not await product_service.get_product_by_id(db, product_id): raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado para actualizar")
    return await product_service.update_product(db, product_id=product_id, product_in=product_in)
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_product(product_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    if not await product_service.delete_product(db, product_id=product_id): raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado para eliminar")