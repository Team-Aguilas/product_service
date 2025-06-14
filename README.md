# Product Service - FastAPI Backend

Este módulo define una capa de servicios asincrónica para la gestión de productos en una base de datos MongoDB utilizando `motor`, el driver asíncrono oficial para MongoDB en Python.

## 📂 Ubicación

`app/services/product_service.py`

## 🚀 Funcionalidades principales

Este archivo proporciona funciones CRUD para trabajar con productos en la colección `products`.

### 📋 Operaciones disponibles

- **`get_all_products(db, skip=0, limit=20)`**  
  Retorna una lista paginada de productos.

- **`get_product_by_id(db, product_id)`**  
  Busca un producto por su ID. Devuelve `None` si no lo encuentra o si el ID no es válido.

- **`create_product(db, product_in)`**  
  Crea un nuevo producto y lo guarda en la base de datos. Retorna el producto creado.

- **`update_product(db, product_id, product_in)`**  
  Actualiza un producto existente si el ID es válido y los datos a actualizar están presentes.

- **`delete_product(db, product_id)`**  
  Elimina un producto por su ID. Retorna `True` si se eliminó correctamente.

## 🧱 Modelos utilizados

Los modelos provienen de `app.models` y se espera que estén definidos como:

- `ProductCreate`
- `ProductUpdate`
- `ProductInDB`

> Asegúrate de que estos modelos usen `pydantic.BaseModel` y estén configurados para soportar el trabajo con MongoDB (`ObjectId`, `alias`, etc.).

## 🛠 Requisitos

- Python 3.10+
- `motor`
- `pydantic`
- `bson`

## 📌 Notas

- Todas las funciones son **asincrónicas** (`async def`) para compatibilidad con FastAPI y el driver `motor`.
- Los IDs deben ser compatibles con `ObjectId`.

## ✅ Ejemplo de uso

```python
from app.services.product_service import get_all_products

products = await get_all_products(db)
