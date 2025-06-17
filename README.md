# Servicio de Productos - Marketplace API

Este microservicio es parte de la aplicación "Marketplace de Frutas y Verduras". Su única responsabilidad es gestionar todas las operaciones relacionadas con los productos (CRUD: Crear, Leer, Actualizar, Eliminar).

## Características Principales

-   Crear nuevos productos.
-   Obtener la lista de todos los productos con paginación.
-   Obtener los detalles de un producto específico por su ID.
-   Actualizar la información de un producto.
-   Eliminar un producto.
-   Servir las imágenes de los productos desde un directorio estático.

## Tecnologías Utilizadas

-   **Framework:** FastAPI
-   **Base de Datos:** MongoDB (a través de Motor)
-   **Lenguaje:** Python 3.11+
-   **Validación de Datos:** Pydantic

## Configuración y Puesta en Marcha

### Prerrequisitos

-   Python 3.11 o superior.
-   Una instancia de MongoDB corriendo.
-   Tener el código del `common/` en el directorio raíz del proyecto.

### 1. Configuración del Entorno

Este servicio se ejecuta desde la raíz del monorepo (`market_place_project/`).

1.  **Variables de Entorno:**
    Crea un archivo `.env` en la raíz de este servicio (`products_service/.env`) con el siguiente contenido:
    ```env
    PROJECT_NAME="Servicio de Productos"
    MONGO_URI="mongodb://localhost:27017/"
    MONGO_DB_NAME="marketplace_db"
    ```

2.  **Dependencias:**
    Se recomienda usar un entorno virtual. Desde la raíz del proyecto (`market_place_project/`), instala las dependencias:
    ```bash
    # Activa tu entorno virtual principal si tienes uno
    pip install -r products_service/requirements.txt
    ```

### 2. Ejecución del Servicio

Para ejecutar el servidor, abre una terminal en la **carpeta raíz del proyecto (`market_place_project/`)** y sigue estos pasos:

1.  **Activa tu entorno virtual.**

2.  **Configura el `PYTHONPATH`** para que Python pueda encontrar el código compartido en `common/`:
    *(Recuerda hacerlo en cada nueva sesión de terminal)*
    ```powershell
    # En Windows (PowerShell)
    $env:PYTHONPATH="."
    ```
    ```bash
    # En Linux o macOS
    export PYTHONPATH="."
    ```

3.  **Inicia el servidor Uvicorn** en el puerto `8001`:
    ```bash
    uvicorn products_service.app.main:app --reload --port 8001
    ```

### Documentación de la API

Una vez que el servicio esté corriendo, la documentación interactiva (Swagger UI) estará disponible en:

[http://localhost:8001/docs](http://localhost:8001/docs)