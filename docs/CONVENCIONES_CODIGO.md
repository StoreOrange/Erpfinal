# Convenciones simples de codigo

Este documento define reglas sencillas para que el codigo se mantenga ordenado.
No son reglas complicadas. Son acuerdos basicos para trabajar como equipo.

## 1. Nombres claros

Usar nombres que expliquen lo que hace cada cosa.

Correcto:

```text
fetchSalesInvoices
createQuoteRequest
voidSalesInvoice
```

Evitar:

```text
data1
funcionNueva
temp
```

## 2. Un archivo, una responsabilidad principal

Cada archivo deberia tener una funcion clara.

Ejemplos:

- `sales.js`: llamadas de ventas.
- `reports.js`: llamadas de informes.
- `procurement.py`: rutas de compras operativas.
- `user.py`: modelos relacionados con usuarios.

## 3. Comentarios utiles

Los comentarios deben explicar la razon, no repetir lo obvio.

Correcto:

```python
# El administrador siempre conserva todos los permisos del catalogo.
```

Evitar:

```python
# Se crea una variable llamada total.
```

## 4. No mezclar frontend con backend

El frontend muestra pantallas y llama servicios.

El backend valida datos, guarda informacion y responde a la API.

## 5. Cada modulo nuevo debe registrar permisos

Cuando se cree un modulo nuevo, tambien se deben agregar sus permisos en:

```text
backend/app/routers/access.py
backend/app/main.py
```

Esto evita que el sistema crezca sin control de acceso.

## 6. Validar antes de entregar

Comandos recomendados:

```powershell
npm run build
```

```powershell
python -m py_compile backend/app/routers/sales.py
```

El comando de Python se puede cambiar por el archivo que se haya modificado.

## 7. No borrar logica sin revisar

Si una funcion no se entiende, primero buscar donde se usa:

```powershell
rg "nombre_de_la_funcion"
```

Luego se decide si se modifica, se mueve o se deja igual.

## 8. Estilo recomendado para este proyecto

El codigo debe verse:

- Claro.
- Ordenado.
- Facil de explicar.
- Sin cambios innecesarios.
- Con nombres entendibles.

La meta no es hacerlo complicado. La meta es que funcione y que se pueda
defender en una presentacion.
