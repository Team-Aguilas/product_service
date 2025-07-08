# Marketplace de Frutas y Verduras (Arquitectura de Microservicios)

Este es un proyecto full-stack para una aplicación de marketplace, diseñado con una arquitectura de microservicios en el backend y una interfaz de usuario moderna en el frontend.

## Arquitectura del Proyecto

El proyecto está dividido en tres componentes principales que se ejecutan de forma independiente:

-   **`products_service`**: Un microservicio de FastAPI (Python) que maneja toda la lógica de productos: CRUD, subida de imágenes y autorización por propietario.
-   **`users_service`**: Un microservicio de FastAPI (Python) que maneja el registro de usuarios, la autenticación (login) y la generación de tokens JWT.
-   **`frontend`**: Una aplicación de React (JavaScript) construida con Vite y Material-UI que consume los dos servicios de backend para proporcionar la interfaz de usuario.
-   **`common`**: Un directorio que contiene el código compartido (modelos Pydantic) utilizado por ambos servicios de backend.

## Tecnologías Utilizadas

-   **Backend**: Python, FastAPI, Motor, Pydantic, Uvicorn
-   **Frontend**: React, Vite, Material-UI (MUI), Axios
-   **Base de Datos**: MongoDB
-   **Autenticación**: JWT (python-jose), Passlib (bcrypt)

## Prerrequisitos

Asegúrate de tener instalado lo siguiente en tu sistema:
-   Python 3.11+ y pip
-   Node.js 18.x+ y npm
-   MongoDB Server (corriendo localmente o en un servicio como MongoDB Atlas)

## Guía de Instalación y Configuración

1.  **Clonar el Repositorio (si aplica):**
    ```bash
    git clone <url-del-repositorio>
    cd market_place_project
    ```

2.  **Entorno Virtual de Python:**
    Se recomienda usar un único entorno virtual en la raíz del proyecto.
    ```bash
    python -m venv venv
    .\venv\Scripts\Activate  # En Windows (PowerShell)
    # source venv/bin/activate  # En Linux/macOS
    ```

3.  **Instalar Dependencias del Backend:**
    Instala los requerimientos para ambos servicios:
    ```bash
    pip install -r products_service/requirements.txt
    pip install -r users_service/requirements.txt
    ```

4.  **Instalar Dependencias del Frontend:**
    ```bash
    cd frontend
    npm install
    cd ..
    ```

5.  **Configurar Variables de Entorno:**
    Crea un archivo `.env` dentro de `products_service` y otro dentro de `users_service` con el siguiente contenido:

    -   **`products_service/.env`**:
        ```env
        PROJECT_NAME="Servicio de Productos"
        MONGO_URI="mongodb://localhost:27017/"
        MONGO_DB_NAME="marketplace_db"
        SECRET_KEY="tu_clave_secreta_muy_larga_y_segura_aqui"
        ALGORITHM="HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES=30
        ```

    -   **`users_service/.env`**:
        ```env
        PROJECT_NAME="Servicio de Usuarios"
        MONGO_URI="mongodb://localhost:27017/"
        MONGO_DB_NAME="marketplace_db"
        SECRET_KEY="tu_clave_secreta_muy_larga_y_segura_aqui"
        ALGORITHM="HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES=30
        ```
    **Importante:** La `SECRET_KEY` debe ser idéntica en ambos archivos.

## Cómo Ejecutar la Aplicación Completa

Necesitarás **tres terminales** separadas, todas ubicadas en la carpeta raíz (`market_place_project/`).

#### **Terminal 1: Iniciar Servicio de Productos**
```powershell
# Activa el entorno virtual
.\venv\Scripts\Activate

# Configura el PYTHONPATH para encontrar la carpeta 'common'
$env:PYTHONPATH="."

# Inicia el servidor en el puerto 8001
uvicorn products_service.app.main:app --reload --port 8001
```

#### **Terminal 2: Iniciar Servicio de Usuarios**
```powershell
# Activa el entorno virtual
.\venv\Scripts\Activate

# Configura el PYTHONPATH (necesario en cada terminal)
$env:PYTHONPATH="."

# Inicia el servidor en el puerto 8002
uvicorn users_service.app.main:app --reload --port 8002
```

#### **Terminal 3: Iniciar Frontend**
```powershell
# Navega a la carpeta del frontend
cd frontend

# Inicia el servidor de desarrollo de Vite
npm run dev
```

### Acceso a la Aplicación

-   **Frontend**: Abre tu navegador en la URL que indique Vite (usualmente `http://localhost:5173`).
-   **Documentación API Productos**: `http://localhost:8001/docs`
-   **Documentación API Usuarios**: `http://localhost:8002/docs`