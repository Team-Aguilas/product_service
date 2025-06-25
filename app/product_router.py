from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
import shutil
import uuid 
from .dependencies import get_db, get_current_active_user # Importa el dependency de usuario
from common.models import ProductCreate, ProductRead, ProductUpdate, UserInDB # Importa UserInDB
from . import product_service

router = APIRouter()

UPLOAD_DIRECTORY = "products_service/static/images"

@router.post("/upload-image", status_code=status.HTTP_201_CREATED)
async def upload_image(file: UploadFile = File(...), user: UserInDB = Depends(get_current_active_user)):
    # Genera un nombre de archivo único para evitar sobreescribir imágenes
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = f"{UPLOAD_DIRECTORY}/{unique_filename}"
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"No se pudo guardar la imagen: {e}")
    finally:
        file.file.close()
    image_url = f"/static/images/{unique_filename}"
    return {"image_url": image_url}

@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_new_product(
    product_in: ProductCreate, 
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
    ):
    return await product_service.create_product(db, product_in=product_in, owner_id=current_user.id)
@router.get("/", response_model=List[ProductRead])
async def read_all_products(skip: int = 0, limit: int = 20, db: AsyncIOMotorDatabase = Depends(get_db)):
    return await product_service.get_all_products(db, skip=skip, limit=limit)
@router.get("/{product_id}", response_model=ProductRead)
async def read_product_by_id(product_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    product = await product_service.get_product_by_id(db, product_id=product_id)
    if not product: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return product
@router.put("/{product_id}", response_model=ProductRead)
async def update_existing_product(
    product_id: str, 
    product_in: ProductUpdate, 
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user) # <-- 1. Requiere login para editar
):
    product = await product_service.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    if product.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para editar este producto")
    return await product_service.update_product(db, product_id=product_id, product_in=product_in)

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_product(
    product_id: str, 
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user) # <-- 1. Requiere login para borrar
):
    product = await product_service.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    if product.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para eliminar este producto")
    await product_service.delete_product(db, product_id=product_id)