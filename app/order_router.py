# products_service/app/order_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from pydantic import BaseModel
from datetime import datetime
from bson import ObjectId

from .dependencies import get_current_user, get_products_collection
from .product_service import get_product_by_id

router = APIRouter(tags=["orders"])

# Endpoint de prueba simple
@router.get("/test")
async def test_endpoint():
    """Endpoint de prueba para verificar que el router funciona"""
    return {"message": "Orders router working!", "status": "ok"}

class OrderItem(BaseModel):
    product_id: str
    quantity: int
    price: float
    product_name: str

class OrderCreate(BaseModel):
    items: List[OrderItem]

class OrderResponse(BaseModel):
    id: str
    user_id: str
    items: List[OrderItem]
    total_amount: float
    status: str
    created_at: datetime

@router.post("/create", response_model=dict)
async def create_order(
    order_data: OrderCreate,
    current_user: dict = Depends(get_current_user),
    products_collection = Depends(get_products_collection)
):
    """
    Crear un nuevo pedido y actualizar el stock de los productos.
    Cualquier usuario autenticado puede realizar pedidos.
    """
    try:
        total_amount = 0
        validated_items = []
        
        # Validar cada item del pedido
        for item in order_data.items:
            # Obtener el producto actual
            try:
                product = await get_product_by_id(item.product_id)
            except Exception:
                raise HTTPException(
                    status_code=404,
                    detail=f"Producto {item.product_name} no encontrado"
                )
            
            # Validar stock disponible
            if product["stock"] < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Stock insuficiente para {item.product_name}. "
                           f"Stock disponible: {product['stock']}, solicitado: {item.quantity}"
                )
            
            # Calcular total
            total_amount += item.price * item.quantity
            validated_items.append(item)
        
        # Actualizar stock de todos los productos
        for item in validated_items:
            product = await get_product_by_id(item.product_id)
            new_stock = product["stock"] - item.quantity
            
            # Actualizar stock en la base de datos
            result = await products_collection.update_one(
                {"_id": ObjectId(item.product_id)},
                {"$set": {"stock": new_stock}}
            )
            
            if result.modified_count == 0:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error al actualizar stock del producto {item.product_name}"
                )
        
        # Crear el registro del pedido (opcional, para historial)
        order_doc = {
            "user_id": current_user["user_id"] if isinstance(current_user, dict) else str(current_user.id),
            "items": [item.dict() for item in validated_items],
            "total_amount": total_amount,
            "status": "completed",
            "created_at": datetime.utcnow()
        }
        
        # Aquí podrías guardar el pedido en una colección de orders si quieres
        # orders_collection = get_orders_collection()
        # order_result = await orders_collection.insert_one(order_doc)
        
        return {
            "message": "Pedido procesado exitosamente",
            "total_amount": total_amount,
            "items_count": len(validated_items),
            "order_id": str(ObjectId())  # Generar un ID temporal
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.get("/my-orders")
async def get_user_orders(current_user: dict = Depends(get_current_user)):
    """
    Obtener los pedidos del usuario actual.
    Nota: Esto requeriría una colección separada de orders.
    """
    # Por ahora retornamos un mensaje informativo
    return {
        "message": "Funcionalidad de historial de pedidos no implementada aún",
        "user_id": current_user["user_id"]
    }
