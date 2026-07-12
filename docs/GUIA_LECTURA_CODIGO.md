# Guia para leer el codigo

Esta guia explica el sistema en palabras simples. La idea es que el proyecto se
pueda presentar, revisar y mantener sin perderse entre muchos archivos.

## 1. Como entra el usuario al sistema

El usuario abre el frontend en el navegador:

```text
http://localhost:5310
```

La pantalla de login esta en:

```text
frontend/src/views/auth/LoginView.vue
```

Cuando el usuario inicia sesion, el frontend llama al backend por medio de:

```text
frontend/src/services/auth.js
```

El backend valida las credenciales en:

```text
backend/app/routers/auth.py
```

## 2. Como funciona una pantalla

Una pantalla normalmente tiene tres partes:

1. Template: lo que se ve.
2. Script: datos, funciones y acciones.
3. Style: estilos propios de la pantalla.

Ejemplo:

```text
frontend/src/views/sales/SalesView.vue
```

## 3. Como una pantalla llama al backend

Las pantallas no deberian llamar directamente a `fetch`. Para mantener orden se
usa una capa de servicios.

Ejemplo:

```text
frontend/src/views/reports/ReportsView.vue
```

usa:

```text
frontend/src/services/reports.js
```

y ese servicio llama a:

```text
backend/app/routers/reports.py
```

## 4. Como se agregan nuevas opciones al menu

Cuando se agrega una pantalla nueva se debe revisar:

```text
frontend/src/router/routes.js
frontend/src/layouts/AppShell.vue
backend/app/routers/access.py
backend/app/main.py
```

Esto es importante porque cada modulo debe tener ruta, menu y permisos.

## 5. Como se agregan permisos

Los permisos se registran en dos lugares:

```text
backend/app/routers/access.py
backend/app/main.py
```

La regla del sistema es:

- Todo modulo nuevo debe tener permisos.
- El rol administrador siempre debe tener acceso completo.
- Los permisos ayudan a controlar que puede ver o hacer cada usuario.

## 6. Como se organiza un modulo completo

Un modulo completo normalmente tiene:

```text
backend/app/models/nombre_modulo.py
backend/app/schemas/nombre_modulo.py
backend/app/routers/nombre_modulo.py
frontend/src/services/nombre_modulo.js
frontend/src/views/nombre_modulo/NombreModuloView.vue
```

No todos los modulos necesitan todos estos archivos, pero esta estructura ayuda
a mantener el proyecto entendible.

## 7. Recomendacion para estudiantes

Antes de modificar una parte del sistema conviene seguir estos pasos:

1. Buscar la pantalla en `frontend/src/views`.
2. Buscar el servicio en `frontend/src/services`.
3. Buscar el router del backend en `backend/app/routers`.
4. Revisar modelos y schemas si se guardan datos.
5. Probar con `npm run build` y `python -m py_compile` cuando aplique.

## 8. Frase guia del proyecto

Primero entender, luego modificar.

Esa regla evita romper logica que ya funciona.
