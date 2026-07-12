# Estructura del proyecto

Este documento explica como esta organizado el sistema. La intencion es que
cualquier estudiante, docente o desarrollador pueda ubicarse rapido dentro del
codigo.

## Vista general

```text
ERP_System/
├── backend/
├── frontend/
├── deploy/
├── docs/
├── compose.yaml
├── .env.example
└── README.md
```

## Carpeta `backend`

Contiene el servidor del sistema. Aqui vive la logica principal, los modelos de
base de datos y las funciones de API que consume la interfaz.

```text
backend/
├── app/
│   ├── core/       Funciones internas de apoyo
│   ├── models/     Tablas y entidades de base de datos
│   ├── routers/    Rutas de la API
│   ├── schemas/    Estructuras de entrada y salida
│   ├── config.py   Configuracion general
│   ├── database.py Conexion a base de datos
│   └── main.py     Punto de inicio del backend
├── alembic/        Migraciones de base de datos
└── requirements.txt
```

### Como leer el backend

1. `main.py` inicia la aplicacion y registra los modulos.
2. `models/` define las tablas.
3. `schemas/` define como viajan los datos.
4. `routers/` contiene las funciones que responden a cada URL.
5. `database.py` conecta FastAPI con PostgreSQL.

## Carpeta `frontend`

Contiene la interfaz del sistema. Aqui estan las pantallas que usa el usuario.

```text
frontend/
├── src/
│   ├── config/     Configuracion del frontend
│   ├── data/       Datos fijos de navegacion
│   ├── layouts/    Estructura visual general
│   ├── router/     Rutas internas de Vue
│   ├── services/   Funciones para llamar al backend
│   ├── theme/      Tema visual
│   ├── views/      Pantallas del sistema
│   ├── App.vue
│   └── main.js
├── Dockerfile
└── package.json
```

### Como leer el frontend

1. `main.js` arranca Vue.
2. `router/routes.js` define las paginas.
3. `layouts/AppShell.vue` contiene el menu lateral y la base visual.
4. `views/` contiene las pantallas.
5. `services/` contiene llamadas al backend.

## Carpeta `deploy`

Contiene scripts para instalar, actualizar o ejecutar el sistema en la VPS.

Esta carpeta no deberia mezclarse con la logica de negocio. Su responsabilidad
es ayudar al despliegue.

## Carpeta `docs`

Contiene documentos de apoyo, bitacoras, explicaciones y guias del proyecto.

Esta carpeta sirve para que el proyecto sea entendible, no solo funcional.

## Regla simple de organizacion

Cada modulo debe intentar mantener esta forma:

```text
Modelo en backend/app/models/
Schema en backend/app/schemas/
Ruta/API en backend/app/routers/
Servicio frontend en frontend/src/services/
Vista frontend en frontend/src/views/
Permisos en backend/app/routers/access.py y backend/app/main.py
```

Ejemplo:

```text
Compras operativas
├── backend/app/models/procurement.py
├── backend/app/schemas/procurement.py
├── backend/app/routers/procurement.py
├── frontend/src/services/procurement.js
└── frontend/src/views/procurement/ProcurementView.vue
```
