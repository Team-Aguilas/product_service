from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
import shutil
import uuid 
from .dependencies import get_db, get_current_active_user, get_current_user # Importa el dependency de usuario
from common.models import ProductCreate, ProductRead, ProductUpdate, UserInDB, RatingCreate, RatingRead, RatingInput, ProductPage # Importa UserInDB
from . import product_service
from typing import List, Optional
import os
from bson import ObjectId
from pydantic import BaseModel

router = APIRouter()


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # llega a product_service/
UPLOAD_DIRECTORY = os.path.join(BASE_DIR, "static", "images")

# Asegurar que el directorio de carga existe
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
print(f"UPLOAD_DIRECTORY configurado en: {UPLOAD_DIRECTORY}")

# UPLOAD_DIRECTORY = os.path.join(os.getcwd(), "products_service", "static", "images")

# UPLOAD_DIRECTORY = "products_service/static/images"

@router.post("/upload-image", status_code=status.HTTP_201_CREATED)
async def upload_image(file: UploadFile = File(...), user: UserInDB = Depends(get_current_active_user)):
    # Genera un nombre de archivo único para evitar sobreescribir imágenes
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIRECTORY, unique_filename)
    
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

@router.get("/", response_model=ProductPage) # Antes era List[ProductRead]
async def read_all_products(
    db: AsyncIOMotorDatabase = Depends(get_db),
    search: Optional[str] = None,
    category: Optional[str] = None,
    sort_by: Optional[str] = None,
    skip: int = 0,
    limit: int = 3 # Recomendado para grids
):
    # La llamada al servicio ya está bien, no necesita cambios
    return await product_service.get_all_products(
        db, search=search, category=category, sort_by=sort_by, skip=skip, limit=limit
    )

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

# Rutas para el sistema de calificaciones
@router.post("/{product_id}/ratings", response_model=RatingRead, status_code=status.HTTP_201_CREATED)
async def create_product_rating(
    product_id: str,
    rating_input: RatingInput,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Crear o actualizar una calificación para un producto."""
    # Verificar que el producto existe
    product = await product_service.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    
    # Crear el objeto RatingCreate con todos los campos necesarios
    rating_create = RatingCreate(
        rating=rating_input.rating,
        comment=rating_input.comment,
        product_id=product.id
    )
    
    return await product_service.create_rating(db, rating_in=rating_create, user_id=current_user.id)

@router.get("/{product_id}/ratings", response_model=List[RatingRead])
async def get_product_ratings(
    product_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Obtener todas las calificaciones de un producto."""
    return await product_service.get_product_ratings(db, product_id)

@router.get("/{product_id}/ratings/me", response_model=RatingRead)
async def get_my_rating_for_product(
    product_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Obtener mi calificación para un producto específico."""
    rating = await product_service.get_user_rating_for_product(db, product_id, current_user.id)
    if not rating:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No has calificado este producto")
    return rating

# Modelo para actualización de stock desde carrito
class CartStockUpdate(BaseModel):
    product_id: str
    new_stock: int

@router.post("/cart/update-stock", status_code=status.HTTP_200_OK)
async def update_stock_from_cart(
    updates: List[CartStockUpdate],
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Endpoint especial para actualizar stock desde el carrito.
    Permite a cualquier usuario autenticado actualizar el stock de productos.
    """
    try:
        updated_products = []
        
        for update in updates:
            # Validar que el producto existe
            product = await product_service.get_product_by_id(update.product_id)
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail=f"Producto {update.product_id} no encontrado"
                )
            
            # Actualizar stock directamente en la base de datos
            result = await db["products"].update_one(
                {"_id": ObjectId(update.product_id)},
                {"$set": {"stock": update.new_stock}}
            )
            
            if result.modified_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"No se pudo actualizar el stock del producto {update.product_id}"
                )
            
            updated_products.append({
                "product_id": update.product_id,
                "previous_stock": product["stock"],
                "new_stock": update.new_stock,
                "status": "updated"
            })
        
        return {
            "message": "Stock actualizado exitosamente",
            "updated_products": updated_products,
            "total_updated": len(updated_products)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error actualizando stock: {str(e)}"
        )