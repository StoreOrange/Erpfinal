# Creditos y notas del proyecto

Este documento deja constancia sencilla del equipo y del enfoque usado en el
codigo.

## Creditos

- Hecho por Carlos.
- Colaboracion academica: Oded Garcia.
- Colaboracion academica: Carlos Ramirez.

## Enfoque de organizacion

El proyecto se intenta mantener con una estructura simple:

- Modelos para representar tablas.
- Rutas del servidor para exponer funciones de la API.
- Esquemas para ordenar datos de entrada y salida.
- Servicios de la interfaz para llamar al servidor.
- Vistas de la interfaz para mostrar pantallas.

## Recordatorio para presentar el sistema

El sistema no busca verse complicado. Busca verse claro, entendible y funcional.

Una buena explicacion para defensa seria:

> El proyecto fue organizado por modulos. Cada modulo tiene una parte de backend
> y una parte de frontend. Ademas, cada modulo importante registra permisos para
> que el administrador pueda controlar los accesos.

## Modulos principales

- Autenticacion.
- Usuarios y permisos.
- Inventario.
- Ventas y facturacion.
- Cierre de caja.
- Informes.
- Compras operativas.
- Configuracion general.

## Nota para futuros cambios

Antes de agregar una funcionalidad nueva, revisar:

1. Donde va la pantalla.
2. Que endpoint necesita.
3. Que modelo o tabla usa.
4. Que permiso debe tener.
5. Como se va a probar.

Esto ayuda a que el sistema siga ordenado aunque crezca.
