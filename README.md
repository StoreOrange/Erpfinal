# Sistema ERP para gestion empresarial

Este proyecto es un sistema ERP desarrollado como aplicacion web. La idea
principal es centralizar procesos de inventario, ventas, compras, usuarios,
permisos e informes en una sola plataforma.

El codigo esta separado en dos partes principales:

- `backend`: API, base de datos, modelos y reglas del sistema.
- `frontend`: pantallas, formularios y navegacion del usuario.

## Objetivo del proyecto

Construir una solucion sencilla pero completa para administrar operaciones de
una empresa. El sistema busca que el usuario pueda:

- Registrar productos e inventario.
- Realizar ventas y facturacion.
- Gestionar usuarios, roles y permisos.
- Consultar informes para la toma de decisiones.
- Registrar compras operativas y solicitudes de cotizacion.

## Tecnologias usadas

- Python con FastAPI para el backend.
- Vue 3 con Vite para el frontend.
- PostgreSQL como base de datos.
- Docker Compose para levantar el entorno completo.

## Estructura rapida

```text
ERP_System/
├── backend/      Codigo del servidor y base de datos
├── frontend/     Codigo de la interfaz web
├── deploy/       Scripts para VPS y despliegue
├── docs/         Documentacion del proyecto
├── compose.yaml  Servicios Docker
└── README.md     Guia principal del proyecto
```

## Iniciar en desarrollo

Requisito principal:

- Docker Desktop con Docker Compose.

Comando para levantar el sistema:

```powershell
docker compose up --build
```

Servicios locales:

- Interfaz web: http://127.0.0.1:5310
- Servidor/API: http://127.0.0.1:8011
- Documentacion API: http://127.0.0.1:8011/docs
- PostgreSQL: `127.0.0.1:5433`

## Comandos utiles

```powershell
# Levantar servicios en segundo plano
docker compose up --build -d

# Ver logs
docker compose logs -f

# Reiniciar solo frontend
docker compose restart frontend

# Reiniciar solo backend
docker compose restart backend

# Detener contenedores sin borrar datos
docker compose down

# Reiniciar base de datos local desde cero
docker compose down -v
docker compose up --build
```

## Documentos recomendados

- [Estructura del proyecto](docs/ESTRUCTURA_PROYECTO.md)
- [Guia para leer el codigo](docs/GUIA_LECTURA_CODIGO.md)
- [Convenciones simples](docs/CONVENCIONES_CODIGO.md)
- [Creditos y notas](docs/CREDITOS_Y_NOTAS.md)
- [Bitacora](docs/BITACORA.md)

## Nota de seguridad

Antes de usar el sistema en produccion se deben cambiar las variables sensibles
del archivo `.env`, especialmente:

- `JWT_SECRET_KEY`
- `POSTGRES_PASSWORD`

El archivo `.env.example` sirve como plantilla.
