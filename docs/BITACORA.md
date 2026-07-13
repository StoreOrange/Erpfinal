# Bitacora del sistema de planificacion de recursos empresariales

Ultima actualizacion: 2026-07-13

## Objetivo

Construir un sistema de planificacion de recursos empresariales modular para
Orange Tec tomando como base funcional el sistema HollywoodPacas. Integra
autenticacion, inventario, produccion, configuracion empresarial y una interfaz
de ventas en evolucion, orientado a pymes, emprendimientos y negocios locales.

## Documento complementario por sprints

Se agrego la bitacora extendida por modulos y sprints en:

- [Bitacora_Sprint.md](./Bitacora_Sprint.md)

Este documento organiza el desarrollo bajo la estructura: problema a resolver,
objetivos, actividades, requerimientos funcionales, requerimientos no
funcionales, analisis, diseno, implementacion, evidencias, validacion,
retroalimentacion y resultados.

## Historial verificado

### 2026-06-06 - Catalogo de vendedores y accesos por sucursal/bodega

- Nuevas entidades persistentes: `sucursales`, `vendedores` y `user_access_profiles`.
- Relacion de `bodegas` con sucursal mediante `sucursal_id`.
- Router backend `/access` para usuarios, roles, sucursales, vendedores y perfiles de acceso.
- Usuario administrador inicial con perfil de acceso principal y vendedor vinculado.
- Respuesta de sesion extendida con accesos activos y vendedor asociado.
- Pantalla `Usuarios y accesos` reemplazada por gestion real con pestañas:
  usuarios, vendedores, sucursales y accesos.
- Ventas consume el catalogo real de vendedores y permite crear vendedores persistentes.
- Validacion Docker/API: `users=1`, `vendors=1`, `branches=1`, `userAccess=1`.

### 2025-12-02 - Version inicial desde VPS

Commit: `ffadcd3`

- Estructura inicial con FastAPI, SQLAlchemy, Alembic, Vue y Vite.
- Configuracion base de conexion y sesiones de base de datos.
- Modelos `users`, `roles` y relacion N:N `user_roles`.
- Registro, login JWT y consulta del usuario autenticado.
- Migracion inicial
  `5285f6b056a5_create_users_and_roles.py`.
- Primer prototipo frontend con login y pagina de inicio.

### 2026-05-03 - Port de HollywoodPacas y UI modular

Commit: `ebc7966`

- Limpieza de archivos generados `__pycache__` y reglas `.gitignore`.
- Port de catalogos: lineas, segmentos, unidades de medida, marcas, bodegas,
  proveedores y tipos de ingreso y egreso.
- Productos con codigo generado, codigo de barras, tres listas de precios,
  activacion, busqueda y saldos por bodega.
- Inventario con ingresos, egresos, transferencias, kardex y manejo de costos.
- Recetas y produccion con apertura, ejecucion, validacion de existencias y
  reporte.
- Configuracion empresarial con identidad visual, logos, politicas y entornos
  de empresa.
- Datos iniciales creados al iniciar la aplicacion: usuario administrador,
  catalogos principales y configuracion empresarial.
- Script `backend/scripts/import_hollpacas_inventory.py`.
- Nuevo shell Vue con proteccion de rutas, dashboard, usuarios, productos,
  inventario, produccion, ventas y configuraciones.
- Tema PrimeVue, Bootstrap Icons y servicios frontend.
- Script `run_dev.ps1` para desarrollo local.

### 2026-05-13 - Costos y acceso a ventas

Commit: `6973fc1`

- Correccion del manejo de moneda de costos.
- Conversiones USD/C$ condicionadas por configuracion.
- Redireccion `/sales` y `/sales/` hacia el frontend.
- Ajustes al formulario de movimientos.

### 2026-06-01 - Docker completo para desarrollo

Cambios locales verificados:

- `compose.yaml` con PostgreSQL 16, FastAPI y Vue/Vite.
- Dockerfiles, `.dockerignore` y `.env.example`.
- Migraciones Alembic antes de iniciar Uvicorn.
- Volumenes para recarga de codigo.
- Servicios validados:
  - Frontend: `http://127.0.0.1:5174`
  - Backend: `http://127.0.0.1:8001`
  - PostgreSQL: `127.0.0.1:5433`

### 2026-06-01 - Tema visual claro y responsive

- Sustitucion del tema oscuro por blanco y violeta.
- Login rediseñado con portada animada.
- Superficies, tarjetas, bordes, espacios y botones uniformes.
- Tema PrimeVue adaptado.
- Login compacto en pantallas pequeñas.

### 2026-06-01 - Reorganizacion de ventas

- Catalogo a la izquierda; ticket y datos comerciales a la derecha.
- Botones PrimeVue corregidos con propiedad `label`.
- Formulario plegable de cliente y observacion integrada.
- Anchos, margenes y truncamiento normalizados.
- Navegacion movil horizontal compacta.
- Seleccion de cliente y accion `Consumidor final` agrupadas.
- Responsive verificado a `390px`: `scrollWidth=390`, `offenders=0`.

### 2026-06-02 - Tipografia estilo Odoo

- Pila tipografica de Odoo 18 aplicada globalmente:
  `-apple-system`, `BlinkMacSystemFont`, `Segoe UI`, `Roboto`,
  `Helvetica Neue`, `Ubuntu`, `Noto Sans`, `Arial`.
- Titulos con prioridad `SF Pro Display`.
- Orden CSS corregido: Bootstrap antes del tema del sistema.
- Login, ventas, inputs, botones y PrimeVue auditados desde navegador.

### 2026-06-02 - Documentacion consolidada

- Esquema verificado directamente contra PostgreSQL.
- Confirmadas 25 tablas fisicas y 29 claves foraneas.
- Confirmadas 46 operaciones OpenAPI.
- Documentacion actualizada:
  - `docs/BITACORA.md`
  - `docs/SISTEMA.md`
  - `docs/PENDIENTES.md`
  - `docs/BASEDEDATOS.md`
  - `docs/API.md`

### 2026-06-02 - Publicacion sincronizada en GitHub

Commit: `5e38589`

- Consolidacion de Docker, documentacion y experiencia visual.
- Publicacion del mismo commit en `erpfinal/main`,
  `erpfinal/desarrollador-1` y `erpfinal/desarrollador-2`.

### 2026-06-02 - Sesion extendida y header de ventas compacto

Cambios locales verificados:

- Duracion JWT movida a `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`.
- Valor predeterminado de desarrollo: `480` minutos (8 horas).
- Clave JWT movida a `JWT_SECRET_KEY` con fallback local de desarrollo.
- Variables agregadas a `.env.example` y `compose.yaml`.
- Header de ventas compactado:
  - Menor padding exterior.
  - Cajetines KPI de menor altura.
  - Tipografia y separaciones reducidas.
  - Pestañas comerciales mas compactas.
- Token nuevo validado con `28800` segundos de vigencia.
- Header refinado a una sola fila de seis KPIs.
- Header validado con altura de `132px`, cajetines de `42px` y cero
  desbordamientos.
- Segunda limpieza visual de ventas:
  - Header reducido a factura, bodega y total.
  - Pestanas de modulos aun no operativos retiradas de la pantalla.
  - Textos descriptivos repetidos y boton `Combos` sin accion retirados.
  - Resumen del ticket reducido a total de factura, unidades y tasa.
  - Vista verificada en escritorio y movil desde navegador.
- Barra superior `Workspace` retirada del shell autenticado.
- Accion `Salir` trasladada al menu lateral y conservada en responsive movil.
- Identidad visual simplificada con una sola carga `Logo del comercio`.
- Logo comercial aplicado al sidebar en reemplazo del bloque textual y
  sincronizado automaticamente como favicon.
- Reemplazo de logo validado: la nueva carga elimina el archivo anterior para
  evitar residuos en `uploads/business`.
- Encabezado del sidebar refinado:
  - Logo centrado dentro de un cajetin blanco con borde sutil.
  - Nombre comercial y subtitulo centrados bajo la imagen.
  - Boton de colapsar separado del area util del logo.
  - Version movil compacta con logo y nombre en una sola fila.
- Encabezado lateral compactado nuevamente:
  - Cajetin e imagen de menor altura.
  - Margenes verticales reducidos.
  - Flecha de ocultar movida a una fila independiente bajo el encabezado.
- Selector de lista de precios retirado de la interfaz de ventas.
- Ventas usa internamente la lista base de precio `1`.
- Sidebar reducido de `278px` a `232px`.
- Estado colapsado reducido de `92px` a `76px`.
- Navegacion, logo y tarjeta de sesion compactados para el nuevo ancho.
- Interfaz de ventas refinada con estilo POS/Odoo:
  - Paneles mas planos, bordes uniformes y sombra ligera.
  - Total de factura jerarquizado en violeta corporativo.
  - Catalogo de productos con resaltado lateral al seleccionar o pasar cursor.
  - Ticket actual mas compacto, con filas limpias y controles alineados.
  - Datos de factura contenidos en tarjeta comercial mas sobria.
  - Barra inferior de acciones reducida y consistente.
- Interfaz de ventas parametrizada por tipo de negocio:
  - `ecommerce`: lista elegante para catalogo y venta asistida.
  - `supermarket`: grilla de tarjetas para buscar y cargar productos rapido.
  - `hardware`: busqueda general densa por codigo, barra, stock y precio.
  - Configuracion empresarial permite seleccionar la vista activa.
  - Backend normaliza valores legacy hacia las nuevas vistas.
- Tasa de cambio agregada como dato operativo:
  - Tabla `exchange_rates` creada para tasas diarias, mensuales o trimestrales.
  - Endpoints para consultar tasa vigente, listar historial y registrar tasas.
  - Nueva seccion `Tasa de cambio` en Datos y Configuraciones.
  - Ventas deja de usar tasa fija y consume la tasa vigente registrada.
  - Movimientos de inventario y produccion precargan la tasa vigente cuando
    requieren conversiones USD/C$.
- Escala visual global compactada:
  - Tarjetas, paneles, headers internos y modulos reducidos a una escala unica.
  - Menus internos de configuracion y tarjetas de opciones compactados.
  - Inputs, botones, labels y textos normalizados para evitar recuadros enormes.
  - Previews de logo y tarjetas KPI ajustadas a tamanos mas consistentes.
  - Segunda pasada aplicada con selectores especificos y guard final en
    `.app-main` para evitar textos y recuadros sobredimensionados en pantallas
    autenticadas.
- Checkboxes de formularios convertidos a chips compactos sin quiebre de
  linea, incluyendo `Activar al guardar` en Entornos.
- Control de inventario activado en ventas:
  - Busqueda de productos muestra existencia por bodega y bloquea productos
    sin stock suficiente.
  - Cantidades del ticket no pueden superar la existencia disponible.
  - Cambio de bodega limpia el ticket para evitar mezclar saldos.
  - Confirmar venta registra egreso de inventario tipo `Venta` y descuenta
    saldo real.
  - Tipo de egreso `Venta` agregado a catalogos iniciales.
- Facturacion POS y pagos aplicados:
  - Nuevas tablas `sales_invoices`, `sales_invoice_items`, `sales_payments` y
    `sales_sequences`.
  - Nuevo modulo backend `/sales-api` con consecutivo POS, listado y registro
    de facturas.
  - La confirmacion de venta ahora registra factura, detalle, pagos y egreso de
    inventario en una sola transaccion.
  - Venta de contado exige pago completo; credito permite saldo pendiente.
  - Recibo POS en pantalla con resumen de items, pagos, saldo y vuelto.
- Selectores de fecha uniformados:
  - `input[type=date]`, `datetime-local`, `time` y `month` reciben estilo tipo
    Bootstrap 5.
  - Foco, hover, bordes, icono del calendario y escala compacta quedan
    consistentes en ventas, inventario, produccion y configuracion.
- Modal de pagos mejorado:
  - Campo de monto recibe foco automatico al abrir el modal.
  - Monto se muestra con texto grueso y estilo destacado.
  - `Enter` registra el pago aplicado y devuelve el foco al monto.
  - Tarjetas de forma de pago y lista de pagos quedan con acabado visual mas
    profesional.
- Modal de pagos compactado:
  - Objetos, tarjetas, botones, inputs, totales y pagos aplicados reducidos de
    escala.
  - Al abrir el modal se precarga el saldo total de la factura en el monto y
    queda autoseleccionado.
  - `Enter` en monto o referencia aplica el pago; si cubre el total, registra
    la factura POS y abre la impresion del recibo.
  - Reorganizacion de grillas del modal para evitar campos alargados,
    montados o desbordados en escritorio y responsive.
  - Flujo de teclado corregido: primer `Enter` en monto agrega la forma de
    pago; segundo `Enter`, con el monto vacio y el total cubierto, genera la
    factura POS.
- Selector de fecha de ventas redisenado:
  - Control tipo Bootstrap 5 con icono de calendario, foco lila y boton rapido
    `Hoy`.
  - Datepicker propio en Vue con calendario desplegable, navegacion de mes,
    dias de semana, dia actual y fecha seleccionada.
  - Se elimina la dependencia visual del selector nativo basico del navegador.
  - Correccion del campo de fecha en ventas: el calendario ya no queda
    recortado por el contenedor y se retiro la fecha tecnica duplicada del
    boton principal.
  - La fecha visible en ventas, resumen de pago y recibo POS se muestra en
    formato `dd-mm-yyyy`; el valor interno se mantiene como `yyyy-mm-dd` para
    guardar correctamente en backend.
  - Ajuste visual posterior del campo fecha en la informacion de factura:
    ocupa dos columnas, se elimina el boton `Hoy` que comprimía el valor y se
    deja el calendario como selector principal.

### 2026-06-04 - Refuerzo de ingresos y egresos de inventario

- Modulo de ingresos/egresos revisado y reforzado:
  - Solo ingresos por `Compras Locales` permiten editar costo/precio de entrada
    para actualizar costo del producto segun moneda configurada.
  - Los demas tipos de ingreso usan costo vigente del producto y bloquean
    edicion manual de costo.
  - Egresos bloquean la edicion manual de costo en la interfaz; muestran costo
    de referencia del producto.
  - Backend de egresos ignora cualquier costo enviado por API y calcula siempre
    el costo con el producto vigente.
  - Validacion de egreso reforzada para no exceder existencia acumulada del
    producto en la bodega.
  - Al registrar ingreso o egreso se abre reporte del movimiento en pantalla.
  - Historico de movimientos permite abrir reporte de cualquier ingreso/egreso.
  - Reporte imprimible/PDF con documento, fecha, tipo, bodega, proveedor,
    usuario, detalle de productos, costos, totales y afectacion de inventario.
- Revision de guardado de productos:
  - Se confirmo que la base actual no tenia productos guardados y no existia
    POST registrado para el producto indicado por el usuario.
  - El formulario de productos ahora aplica defaults de linea, segmento, unidad
    y bodega inicial cuando corresponde.
  - El boton `Crear producto` ejecuta guardado directo y muestra validaciones
    visibles antes de enviar.
- Selector de fecha de ingresos/egresos reemplazado:
  - Se elimina el `input type=date` nativo del modulo de movimientos.
  - Nuevo calendario visual con icono, fecha `dd-mm-yyyy`, navegacion mensual,
    cierre por clic externo y ajuste responsive.
- Importacion de productos desde base `hollpacas`:
  - Se conecto al PostgreSQL del host mediante `host.docker.internal`.
  - Se importaron 280 productos, 280 saldos, catalogos de lineas, segmentos,
    unidades y bodegas.
  - Se normalizaron productos sin unidad asignandoles `Unidad`.
  - Resultado validado: 280 productos activos, 0 productos sin unidad, 20 saldos
    positivos y existencia total 321.
- Compatibilidad Firefox:
  - Se retiraron selectores CSS `:has()` usados en impresion y modal de pagos.
  - Las reglas de impresion ahora se activan con clases `printing-*` desde Vue.
  - Frontend validado con build y assets principales respondiendo `200`.

### 2026-06-05 - Enfoque empresarial y mejora inicial de inventario

- Se adopta la denominacion visible "sistema de planificacion de recursos
  empresariales" en lugar de presentar el producto con siglas.
- Textos visibles del login, dashboard, recibo POS, shell principal y usuarios
  ajustados a "Sistema empresarial" o equivalentes.
- Inicio de refinamiento UI del modulo de ingresos y egresos:
  - Formulario operativo toma prioridad sobre el historico.
  - Historial documental queda como panel secundario.
  - Buscador de productos con icono, menor altura y estilo mas limpio.
  - Producto seleccionado se muestra en tarjeta compacta con disponibilidad.
  - Totales, campos, botones y espaciados reducidos para una vista mas
    profesional.
  - Correccion de separadores visuales con codificacion danada.

### 2026-06-06 - Arquitectura visual Enterprise fase 1

- Se inicia modernizacion visual global inspirada en Odoo Enterprise, Zoho One,
  SAP Business One Web y Monday.com sin tocar endpoints, rutas ni modelos.
- Frontend:
  - Registro global de `ToastService` y `ConfirmationService`.
  - `Toast` y `ConfirmDialog` disponibles a nivel de aplicacion.
  - Dependencias agregadas: `apexcharts` y `vue3-apexcharts`.
  - Separacion de chunks en Vite para Vue, PrimeVue y graficos.
- Shell principal:
  - Sidebar colapsable conserva rutas actuales.
  - Navegacion agrupada con `PanelMenu`.
  - Header superior fijo con breadcrumb dinamico.
  - `MegaMenu` de acciones rapidas y drawer movil.
- Dashboard:
  - KPIs empresariales por productos, inventario y gestion financiera.
  - Graficos ApexCharts para movimientos y distribucion operativa.
  - Timeline de actividad, tags, skeleton de carga y widgets responsivos.

### 2026-06-06 - Formularios Enterprise fase 2

- Productos:
  - Formulario principal modernizado con `FloatLabel` de PrimeVue.
  - Campos principales de descripcion, codigo de barra, linea, segmento,
    unidad, marca, costos, precios, existencia y bodega inicial alineados al
    patron Enterprise.
  - Validacion visual con `p-invalid` para descripcion, unidad y bodega inicial
    requerida cuando hay existencia.
- Inventario:
  - Filtros de fecha del historico de ingresos/egresos migrados a `DatePicker`
    PrimeVue con icono y formato visual `dd-mm-yyyy`.
  - Se conserva el filtrado interno en formato ISO para no afectar datos ni API.
- Estilos:
  - Reglas globales para `FloatLabel`, `DatePicker` e invalidacion visual en
    formularios del area principal.

### 2026-06-06 - Tablas Enterprise fase 3

- Productos:
  - `DataTable` avanzado con filtro global conectado al buscador existente.
  - Ordenamiento, columnas redimensionables, scroll, paginacion extendida,
    filas alternas y exportacion CSV compatible con Excel.
  - Columnas con `field` para mejorar ordenamiento y exportacion.
- Ingresos y egresos:
  - Historico documental actualizado con exportacion CSV, ordenamiento,
    resize de columnas, scroll, paginacion avanzada y columna de acciones fija.
- Produccion:
  - Historico de producciones y detalle del informe con exportacion CSV,
    ordenamiento, columnas redimensionables, scroll y filas alternas.
- Estilos:
  - Acciones de tabla unificadas con clase `enterprise-table-actions`.
  - Cabeceras de tabla alineadas al estilo Enterprise.

## Estado funcional consolidado

| Frente | Estado actual |
| --- | --- |
| Autenticacion | Registro, login JWT, usuario autenticado y sesion local de 8 horas |
| Configuracion | Datos empresariales, logos, politicas, entornos y tasas de cambio |
| Productos | Catalogos, precios, codigos, busqueda y saldos |
| Inventario | Ingresos, egresos, transferencias y kardex |
| Produccion | Recetas, apertura, ejecucion y reporte |
| Ventas | Interfaz POS responsive con factura, pagos, tasa vigente, control de stock y egreso de inventario |
| Usuarios | Administracion de usuarios, roles, permisos por modulo y administrador con acceso total |
| Reportes | Informes operativos y analiticos para ventas, inventario y comportamiento de productos |
| Compras internas | Solicitudes, cotizaciones, insumos, proveedores y notificaciones por correo |
| Utilidades de facturacion | Reimpresion de facturas POS/carta y anulacion controlada por permisos |
| Desarrollo | Entorno Docker completo con PostgreSQL, backend y frontend |

## Hallazgos tecnicos vigentes

- Alembic contiene la migracion inicial de usuarios y roles. Las tablas de
  inventario y configuracion se materializan actualmente mediante
  `Base.metadata.create_all()` y ajustes de arranque.
- La interfaz de ventas administra temporalmente cliente, vendedor, pagos y
  ticket en frontend; el backend de ventas y su persistencia siguen pendientes.
- Antes de produccion se debe configurar un valor privado y unico para
  `JWT_SECRET_KEY`.

## Validacion actual

- `docker compose ps`: base saludable, backend y frontend activos.
- `docker compose exec -T frontend npm run build`: correcto.
- `git diff --check`: correcto.
- PostgreSQL consultado directamente.
- OpenAPI consultado desde `http://127.0.0.1:8001/openapi.json`.

## Redocumentacion del proceso de desarrollo

Ultima actualizacion documental: 2026-07-13

Esta seccion resume el proceso completo de construccion del sistema para que
pueda usarse como base de un cronograma de actividades, informe academico,
presentacion de avance o defensa del proyecto. El objetivo es dejar evidencia
clara de que el sistema fue desarrollado por etapas, con revision funcional,
validacion tecnica y mejoras iterativas.

### Enfoque de trabajo

El desarrollo se trabajo bajo una metodologia incremental. Primero se levanto
una base funcional minima y luego se agregaron modulos, permisos, reportes,
despliegue y mejoras visuales. Cada etapa dejo entregables verificables:
codigo fuente, pantallas funcionales, servicios backend, tablas de base de
datos, documentacion y pruebas manuales.

El sistema tomo como referencia operativa el flujo de HollywoodPacas, pero fue
adaptado a una estructura mas general de sistema empresarial. Se priorizo que
cada modulo pudiera funcionar localmente antes de enviar cambios a GitHub y
antes de actualizar la VPS.

### Metodologia de desarrollo: Scrum

Para documentar el proyecto se adopta Scrum como metodologia de trabajo. Scrum
es un marco agil que permite construir un sistema por partes pequenas,
revisables y mejorables. En lugar de intentar terminar todo el sistema de una
sola vez, el proyecto se divide en sprints. Cada sprint tiene un objetivo, una
lista de tareas, entregables funcionales, revision y retroalimentacion.

En este proyecto Scrum se usa de forma academica y practica. El equipo trabaja
con avances cortos, valida lo construido, corrige errores y luego continua con
el siguiente modulo. Esta forma de trabajo ayuda mucho en un sistema ERP porque
cada area depende de otra: ventas depende de productos, productos depende de
catalogos, reportes dependen de ventas e inventario, y los permisos afectan a
todo el sistema.

#### Definicion de Scrum aplicada al proyecto

Scrum se entiende en este proyecto como una metodologia incremental para
planificar, construir, revisar y mejorar el sistema. Su uso permite:

- Dividir el desarrollo en sprints.
- Priorizar funcionalidades importantes.
- Entregar avances funcionales por modulo.
- Revisar resultados antes de continuar.
- Documentar cambios y problemas encontrados.
- Ajustar el sistema con base en pruebas y retroalimentacion.
- Mantener evidencia del proceso para revision academica.

#### Roles Scrum del proyecto

| Rol Scrum | Aplicacion dentro del proyecto | Responsabilidad |
| --- | --- | --- |
| Product Owner | Representa la necesidad del negocio y define que debe resolver el sistema | Priorizar modulos, validar funcionalidades y solicitar mejoras |
| Scrum Master | Acompana el proceso de trabajo y ayuda a mantener orden en las actividades | Organizar tareas, remover bloqueos y cuidar que se documente el avance |
| Equipo de desarrollo | Estudiantes/desarrolladores que construyen backend, frontend, base de datos y despliegue | Analizar, programar, probar, corregir, documentar y entregar incrementos |
| Usuario final o interesado | Persona que usara o revisara el sistema | Probar pantallas, dar observaciones y confirmar si el flujo es entendible |
| Tutor o revisor | Figura academica que revisa el avance tecnico y documental | Recomendar ajustes, validar presentacion y orientar mejora del informe |

#### Artefactos Scrum utilizados

| Artefacto | Uso en el proyecto | Evidencia |
| --- | --- | --- |
| Product Backlog | Lista general de funcionalidades necesarias para el ERP | Modulos, pendientes, solicitudes y mejoras documentadas |
| Sprint Backlog | Tareas seleccionadas para trabajar en un periodo corto | Actividades por sprint en la bitacora |
| Incremento | Parte funcional entregada al final de cada sprint | Pantalla, endpoint, tabla, reporte o modulo funcionando |
| Definicion de Terminado | Condiciones minimas para considerar lista una actividad | Codigo funcionando, prueba local, documentacion y commit |
| Bitacora | Registro historico del proceso | Este archivo `docs/BITACORA.md` |
| Repositorio Git | Control de versiones del proyecto | Commits, ramas y cambios enviados a GitHub |

#### Ceremonias Scrum adaptadas

| Ceremonia | Como se aplico | Resultado esperado |
| --- | --- | --- |
| Planificacion del sprint | Se selecciono que modulo o mejora se trabajaria primero | Lista de tareas claras para el sprint |
| Reunion diaria o seguimiento | Se reviso que estaba funcionando, que fallaba y que seguia | Deteccion de bloqueos y prioridades |
| Revision del sprint | Se probo el modulo terminado desde la interfaz o API | Validacion funcional del avance |
| Retrospectiva | Se reviso que se podia mejorar en codigo, interfaz, datos o despliegue | Ajustes para el siguiente sprint |
| Refinamiento del backlog | Se agregaron nuevas solicitudes o se corrigieron pendientes | Backlog mas ordenado y actualizado |

#### Product Backlog general

| ID | Historia o necesidad | Prioridad | Resultado esperado |
| --- | --- | --- | --- |
| PB01 | Como usuario necesito iniciar sesion para proteger el sistema | Alta | Login con autenticacion JWT |
| PB02 | Como administrador necesito gestionar usuarios y permisos | Alta | Roles, permisos y accesos por modulo |
| PB03 | Como encargado necesito registrar productos y catalogos | Alta | Productos, lineas, unidades, bodegas y proveedores |
| PB04 | Como encargado necesito controlar inventario | Alta | Ingresos, egresos, transferencias y kardex |
| PB05 | Como vendedor necesito facturar productos | Alta | POS, ticket, pagos y factura |
| PB06 | Como cajero necesito cerrar caja | Alta | Vales, movimientos y cierre diario |
| PB07 | Como administrador necesito configurar datos del negocio | Media | Logo, tasa, politicas y parametros |
| PB08 | Como gerente necesito reportes para tomar decisiones | Alta | Informes de ventas, inventario y analisis |
| PB09 | Como empresa necesito controlar compras internas | Media | Insumos, solicitudes y cotizaciones |
| PB10 | Como usuario necesito recibir notificaciones por correo | Media | Configuracion SMTP y destinatarios |
| PB11 | Como cajero necesito reimprimir o anular facturas | Alta | Utilidades de facturacion por permisos |
| PB12 | Como equipo necesito desplegar el sistema en VPS | Alta | Docker, Nginx, systemd y actualizacion por Git |
| PB13 | Como equipo necesito documentar el proyecto | Alta | Bitacora, guia de lectura, pendientes y estructura |

#### Definicion de Terminado

Una tarea se considera terminada cuando cumple estas condiciones:

- El codigo fue implementado en el modulo correspondiente.
- La funcionalidad puede abrirse o probarse localmente.
- La pantalla no muestra errores visibles.
- El backend responde correctamente cuando aplica.
- La base de datos guarda o consulta la informacion esperada.
- Los permisos se revisan si la funcionalidad agrega una opcion nueva.
- El frontend compila cuando el cambio afecta la interfaz.
- Se actualiza la documentacion si el cambio modifica el alcance del sistema.
- El cambio queda listo para ser enviado a Git.

#### Sprints del proyecto

| Sprint | Objetivo | Actividades principales | Incremento entregado |
| --- | --- | --- | --- |
| Sprint 1 | Levantar base tecnica del sistema | Crear backend, frontend, conexion a base de datos y autenticacion inicial | Proyecto ejecutable con login base |
| Sprint 2 | Construir catalogos e inventario inicial | Crear productos, bodegas, proveedores, unidades y saldos | Modulo de productos e inventario base |
| Sprint 3 | Controlar movimientos de inventario | Implementar ingresos, egresos, transferencias y kardex | Inventario operativo con historial |
| Sprint 4 | Agregar produccion | Crear recetas, produccion, consumo y reporte | Modulo de produccion integrado al inventario |
| Sprint 5 | Construir ventas POS | Crear pantalla de venta, ticket, cliente, vendedor y pagos | POS funcional en frontend |
| Sprint 6 | Persistir facturacion | Guardar facturas, items, pagos, consecutivo y recibo | Venta guardada y recibo POS |
| Sprint 7 | Mejorar configuracion empresarial | Agregar logo, datos de empresa, tasa de cambio y politicas | Modulo de configuracion |
| Sprint 8 | Reforzar usuarios y permisos | Crear permisos por modulo y acceso total del administrador | Seguridad funcional por roles |
| Sprint 9 | Crear informes | Agregar reportes de ventas, inventario, caja y analisis | Modulo de informes |
| Sprint 10 | Crear compras internas | Agregar insumos, solicitudes, cotizaciones y correos | Modulo de compras internas |
| Sprint 11 | Agregar utilidades de facturacion | Reimpresion y anulacion de facturas por permisos | Submenu de utilidades |
| Sprint 12 | Pulir interfaz | Ajustar login, dashboard, formularios, modales, campos y colores | Interfaz mas clara y presentable |
| Sprint 13 | Preparar despliegue | Crear scripts, servicios systemd, Docker, Nginx y actualizacion | Sistema desplegable en VPS |
| Sprint 14 | Migrar/importar datos | Preparar respaldo e importacion de inventario local hacia nube | Carga de datos documentada |
| Sprint 15 | Documentar y ordenar | Comentar codigo importante, crear guias y ampliar bitacora | Documentacion para revision academica |

#### Sprint Backlog detallado

| Sprint | Tareas incluidas | Dependencias | Evidencias |
| --- | --- | --- | --- |
| Sprint 1 | Configurar FastAPI, Vue, PostgreSQL, Docker, rutas base y login | Ninguna | Backend activo, frontend activo, login visible |
| Sprint 2 | Crear modelos de catalogos, productos, bodegas y formularios de productos | Sprint 1 | Producto creado y listado |
| Sprint 3 | Registrar ingresos/egresos, validar stock y mostrar historial | Sprint 2 | Movimiento registrado y existencia actualizada |
| Sprint 4 | Crear recetas, produccion y reportes de produccion | Sprint 3 | Produccion finalizada y reporte |
| Sprint 5 | Disenar POS, catalogo, ticket, pagos y datos comerciales | Sprint 2, Sprint 3 | Pantalla de ventas funcionando |
| Sprint 6 | Crear tablas de facturas, items, pagos y secuencias | Sprint 5 | Factura guardada con recibo |
| Sprint 7 | Crear configuracion de empresa, logo, tasa y parametros | Sprint 1 | Pantalla de configuracion guardando |
| Sprint 8 | Crear roles, permisos, accesos y proteccion de menus | Sprint 1, Sprint 7 | Usuario con permisos visibles |
| Sprint 9 | Crear endpoints y vistas de reportes | Sprint 3, Sprint 6 | Reportes con datos del sistema |
| Sprint 10 | Crear insumos, solicitudes, cotizaciones y correos | Sprint 8 | Solicitud de compra registrada |
| Sprint 11 | Crear busqueda de facturas, reimpresion y anulacion | Sprint 6, Sprint 8 | Factura anulada o reimpresa |
| Sprint 12 | Ajustar estilos, responsive, modales y dashboard | Sprints anteriores | Capturas antes/despues |
| Sprint 13 | Preparar Git, servicios, Nginx, puertos y scripts VPS | Sistema local estable | Sitio funcionando en nube |
| Sprint 14 | Exportar/importar SQL, respaldar e insertar datos | Sprint 13 | Inventario cargado en VPS |
| Sprint 15 | Ampliar documentacion, bitacora, guias y pendientes | Todo el proyecto | Archivos `.md` completos |

#### Criterios de aceptacion Scrum

| Tipo de entregable | Criterio de aceptacion |
| --- | --- |
| Pantalla frontend | Abre sin errores, muestra datos, permite guardar o consultar y respeta permisos |
| Endpoint backend | Responde correctamente, valida datos y guarda/consulta en PostgreSQL |
| Tabla de base de datos | Tiene campos necesarios, relaciones utiles y permite persistir el proceso |
| Reporte | Muestra informacion filtrada, clara y relacionada con datos reales |
| Permiso | La opcion aparece u oculta segun rol, y administrador conserva acceso total |
| Despliegue | El sistema levanta con Docker y responde desde Nginx o entorno local |
| Documentacion | Explica objetivo, actividad, resultado, evidencia y pendiente si existe |

#### Retrospectivas y aprendizajes por sprint

| Sprint | Aprendizaje | Mejora aplicada |
| --- | --- | --- |
| Sprint 1 | El entorno debe estar estable antes de avanzar | Se uso Docker para backend, frontend y base de datos |
| Sprint 2 | Los catalogos son necesarios antes de productos | Se cargaron datos iniciales para no empezar vacio |
| Sprint 3 | Inventario necesita historial para ser confiable | Se agregaron movimientos y kardex |
| Sprint 4 | Produccion depende de existencias reales | Se conecto con inventario |
| Sprint 5 | Ventas debe ser rapida y visual | Se compacto POS y ticket |
| Sprint 6 | Facturar debe afectar datos reales | Se guardo factura, pagos y egreso de inventario |
| Sprint 7 | La empresa necesita personalizar el sistema | Se agrego configuracion empresarial |
| Sprint 8 | Cada modulo nuevo necesita permisos | Se definio regla de permisos obligatoria |
| Sprint 9 | Los reportes dependen de datos confiables | Se consultan ventas, inventario y caja |
| Sprint 10 | Compras internas tiene flujo diferente a mercaderia | Se separo insumos de productos de venta |
| Sprint 11 | Anular facturas es una accion sensible | Se controla por permisos |
| Sprint 12 | La interfaz debe ser entendible para usuarios | Se ajustaron formularios, modales y colores |
| Sprint 13 | La nube tiene problemas diferentes al local | Se ajustaron puertos, Nginx, Docker y servicios |
| Sprint 14 | Cargar inventario manual es lento | Se preparo importacion SQL |
| Sprint 15 | El proyecto necesita evidencia documental | Se amplio bitacora y guias |

### Fases historicas del desarrollo

| Fase | Actividades principales | Entregables | Estado |
| --- | --- | --- | --- |
| 1. Levantamiento inicial | Revision de necesidades, estructura base del proyecto y definicion de modulos principales | Proyecto FastAPI/Vue, autenticacion inicial, conexion a base de datos | Completado |
| 2. Port funcional | Migracion de catalogos y flujos tomados de HollywoodPacas | Productos, bodegas, proveedores, unidades, inventario y configuracion | Completado |
| 3. Entorno local | Preparacion del ambiente de desarrollo con Docker y scripts locales | `compose.yaml`, backend, frontend y PostgreSQL funcionando localmente | Completado |
| 4. Inventario | Ingresos, egresos, transferencias, kardex y validaciones de existencia | Movimientos de inventario y reportes imprimibles | Completado |
| 5. Ventas | Construccion del punto de venta, busqueda de productos, pagos y factura POS | Pantalla de ventas, control de stock, factura y recibo | Completado |
| 6. Configuracion | Parametros empresariales, logos, politica comercial y tasa de cambio | Modulo de datos empresariales y configuracion | Completado |
| 7. Usuarios y permisos | Mejora del modulo de usuarios, roles y accesos por funcionalidad | Administrador con acceso total, permisos por modulo y control de opciones | Completado |
| 8. Reportes | Incorporacion de informes operativos y analiticos | Reportes de ventas, inventario, productos estancados y mayor movimiento | Completado |
| 9. Compras internas | Creacion de solicitudes, cotizaciones e inventario de insumos | Modulo de compras no mercaderia, proveedores y notificaciones | Completado |
| 10. Utilidades de facturacion | Herramientas para anular y reimprimir facturas | Reimpresion POS/carta y anulacion controlada por permisos | Completado |
| 11. Despliegue VPS | Scripts para actualizar desde Git, servicios systemd, Docker y Nginx | Servicio de actualizacion y despliegue en nube | Completado con ajustes |
| 12. Documentacion | Organizacion del codigo, guias de lectura, bitacora y pendientes | Documentos `.md` para revision academica y soporte tecnico | En mejora continua |

### Cronograma base del desarrollo realizado

| Periodo | Actividad desarrollada | Resultado obtenido |
| --- | --- | --- |
| Semana 1 | Analisis inicial del sistema requerido y revision de HollywoodPacas como referencia | Lista de modulos base y estructura inicial del ERP |
| Semana 2 | Creacion del backend con FastAPI, modelos iniciales, usuarios y roles | API base con autenticacion y migracion inicial |
| Semana 3 | Creacion del frontend con Vue, rutas protegidas, login y shell principal | Interfaz inicial navegable y autenticada |
| Semana 4 | Implementacion de catalogos administrativos e inventario inicial | Productos, bodegas, unidades, proveedores y saldos |
| Semana 5 | Construccion de ingresos, egresos, transferencias y kardex | Control operativo de inventario |
| Semana 6 | Implementacion de produccion, recetas y consumo de insumos | Flujo de produccion integrado con inventario |
| Semana 7 | Diseno y refinamiento del modulo de ventas POS | Pantalla de venta responsive y flujo de ticket |
| Semana 8 | Registro de facturas, pagos, recibos y descuento de inventario | Venta completa con persistencia y afectacion de stock |
| Semana 9 | Configuracion empresarial, logos, tasas de cambio y politicas | Parametros del negocio centralizados |
| Semana 10 | Mejora de usuarios, roles, permisos y accesos por modulo | Seguridad funcional y administrador con acceso total |
| Semana 11 | Incorporacion de reportes operativos y analiticos | Informes para toma de decisiones |
| Semana 12 | Desarrollo de compras internas y cotizaciones | Gestion de insumos y solicitudes de compra |
| Semana 13 | Notificaciones por correo y plantillas operativas | Envio de solicitudes y avisos por email |
| Semana 14 | Utilidades de facturacion: anulacion y reimpresion | Herramientas administrativas para facturas |
| Semana 15 | Preparacion de despliegue en VPS, Nginx, Docker y servicios | Sistema ejecutandose en nube |
| Semana 16 | Documentacion, limpieza visual, bitacora y guias de lectura | Material listo para revision tecnica y academica |

### Actividades tecnicas documentadas

1. Analisis y levantamiento:
   - Identificacion de procesos principales: ventas, inventario, usuarios,
     compras internas, reportes y configuracion.
   - Revision del sistema HollywoodPacas para reutilizar logica probada.
   - Definicion de una estructura modular para evitar mezclar responsabilidades.

2. Diseno:
   - Separacion entre backend, frontend, base de datos y despliegue.
   - Uso de routers por area funcional en FastAPI.
   - Uso de vistas Vue por modulo de negocio.
   - Definicion de permisos para controlar el acceso a cada opcion.

3. Implementacion:
   - Construccion de modelos SQLAlchemy para persistencia.
   - Creacion de endpoints REST para cada proceso.
   - Integracion de servicios frontend para consumir la API.
   - Desarrollo de pantallas operativas con formularios, tablas y modales.

4. Validacion:
   - Pruebas manuales desde navegador.
   - Construccion del frontend con `npm run build`.
   - Revision de contenedores con Docker Compose.
   - Validacion de endpoints principales desde OpenAPI.
   - Pruebas de despliegue y actualizacion en VPS.

5. Documentacion:
   - Bitacora del proyecto.
   - Guia de lectura del codigo.
   - Estructura del proyecto.
   - Pendientes funcionales.
   - Documentacion de usuarios, permisos y modulos principales.

### Cronograma sugerido para implementacion final

Este cronograma puede usarse como base para una presentacion formal del
proyecto o para planificar una entrega final supervisada.

| Semana | Actividad propuesta | Entregable esperado |
| --- | --- | --- |
| 1 | Revision de requerimientos con usuarios finales | Lista validada de requerimientos funcionales y no funcionales |
| 2 | Ajuste del modelo de datos y permisos | Diagrama actualizado y matriz de permisos |
| 3 | Revision completa de inventario y productos | Modulo de inventario validado |
| 4 | Revision completa de ventas y facturacion | Flujo POS validado con anulacion y reimpresion |
| 5 | Revision del modulo de compras internas | Solicitudes, cotizaciones e insumos validados |
| 6 | Revision de reportes gerenciales | Reportes de analisis y exportacion validados |
| 7 | Pruebas integrales del sistema | Lista de errores corregidos y evidencia de pruebas |
| 8 | Preparacion de produccion | Variables de entorno, respaldos, servicios y despliegue final |
| 9 | Capacitacion de usuarios | Manual corto de uso y sesion de entrenamiento |
| 10 | Cierre documental | Informe final, bitacora y anexos tecnicos |

### Relacion con ingenieria de software

La bitacora deja evidencia de un proceso compatible con practicas comunes de
ingenieria de software:

- Analisis de requerimientos antes de construir modulos nuevos.
- Diseno modular para separar ventas, inventario, compras, usuarios y reportes.
- Implementacion incremental para entregar avances funcionales.
- Validacion tecnica mediante pruebas locales, build y despliegue.
- Gestion de versiones con Git para conservar historial de cambios.
- Documentacion continua para facilitar mantenimiento y revision academica.

### Pendientes recomendados para cierre academico

- Preparar matriz de requerimientos funcionales y no funcionales.
- Agregar diagrama entidad-relacion actualizado.
- Agregar diagrama de arquitectura general.
- Documentar casos de uso principales por modulo.
- Crear plan de pruebas con evidencia por pantalla.
- Crear manual corto para usuario administrador.
- Crear manual corto para usuario operativo.
- Definir plan de respaldo y recuperacion de base de datos.
- Validar variables privadas antes de produccion:
  `JWT_SECRET_KEY`, `POSTGRES_PASSWORD` y credenciales SMTP.

### Resumen ejecutivo del avance

El sistema evoluciono desde una base tecnica inicial hasta un sistema
empresarial modular con autenticacion, inventario, ventas, produccion,
configuracion, usuarios, permisos, reportes, compras internas, utilidades de
facturacion y despliegue en VPS. El trabajo se realizo de manera incremental,
validando cada modulo localmente antes de integrarlo al repositorio y preparar
su actualizacion en la nube.

## Bitacora ampliada para cronograma y Gantt

Esta ampliacion esta escrita para que pueda copiarse a una herramienta externa,
un modelo de apoyo o una plantilla academica. Se organiza como actividades de
desarrollo, con descripcion sencilla, resultado esperado, dependencia y posible
evidencia. La redaccion se mantiene clara para que un equipo de estudiantes
pueda explicar que hizo, por que lo hizo y como fue verificando cada avance.

### Estructura de desglose del trabajo

| Codigo | Actividad | Descripcion sencilla | Dependencia | Evidencia sugerida |
| --- | --- | --- | --- | --- |
| A01 | Analisis del problema | Se reviso la necesidad de tener un sistema empresarial para controlar ventas, inventario, usuarios, reportes y compras internas | Ninguna | Documento de requerimientos o resumen del problema |
| A02 | Revision de sistema base | Se reviso HollywoodPacas para identificar flujos ya conocidos y poder reutilizar ideas funcionales | A01 | Comparacion de modulos y pantallas |
| A03 | Definicion de modulos | Se separo el sistema en areas: ventas, inventario, produccion, usuarios, reportes, compras y configuracion | A01, A02 | Lista de modulos del sistema |
| A04 | Preparacion del backend | Se organizo FastAPI con routers, modelos, base de datos y autenticacion | A03 | Carpeta `backend/app`, OpenAPI y endpoints |
| A05 | Preparacion del frontend | Se organizo Vue con rutas, vistas, servicios y shell principal | A03 | Carpeta `frontend/src`, pantallas y rutas |
| A06 | Base de datos inicial | Se prepararon tablas para usuarios, roles y entidades principales del negocio | A04 | Modelos SQLAlchemy y migraciones |
| A07 | Autenticacion | Se implemento login, token JWT, usuario autenticado y sesion local | A04, A05 | Login funcional y endpoints de sesion |
| A08 | Catalogos | Se agregaron lineas, segmentos, unidades, bodegas, proveedores y tipos de movimiento | A06 | Pantallas de catalogos y datos iniciales |
| A09 | Productos | Se implemento registro, busqueda, precios, codigos, estado activo y saldo por bodega | A08 | Pantalla de productos y registros guardados |
| A10 | Inventario | Se implementaron ingresos, egresos, transferencias y kardex | A09 | Movimientos registrados y afectacion de stock |
| A11 | Reportes de inventario | Se agregaron reportes imprimibles de movimientos y consultas historicas | A10 | Reporte de ingreso, egreso o kardex |
| A12 | Produccion | Se implementaron recetas, apertura de produccion, consumo de insumos y reporte | A10 | Produccion registrada y reporte generado |
| A13 | Ventas POS | Se construyo pantalla de ventas con catalogo, ticket, cliente, vendedor y pagos | A09, A10 | Pantalla POS funcionando localmente |
| A14 | Facturacion | Se registro factura, detalle, pagos, saldo, vuelto y consecutivo POS | A13 | Factura guardada y recibo generado |
| A15 | Control de stock en ventas | La venta valida existencia y descuenta inventario al facturar | A10, A14 | Existencia antes/despues de una venta |
| A16 | Configuracion empresarial | Se agregaron datos del negocio, logo, politicas, entornos y tasa de cambio | A05, A06 | Pantalla de configuracion y valores guardados |
| A17 | Usuarios y permisos | Se mejoro el modulo de usuarios para controlar accesos por modulo y opcion | A07, A16 | Pantalla de permisos y roles |
| A18 | Administrador por defecto | Se definio que el administrador siempre tenga acceso completo al sistema | A17 | Usuario administrador con todas las opciones visibles |
| A19 | Reportes operativos | Se agregaron informes para analizar ventas, inventario y actividad del negocio | A10, A14 | Modulo de informes y tablas de resultados |
| A20 | Reportes especiales | Se agregaron reportes de productos estancados, productos con mayor movimiento y analisis de inventario | A19 | Reportes analiticos filtrables |
| A21 | Compras internas | Se creo modulo para solicitudes, cotizaciones e inventario de insumos no mercaderia | A17 | Pantalla de compras internas |
| A22 | Correos de compras | Se agrego estructura para destinatarios, plantillas y envio de notificaciones por correo | A21 | Configuracion SMTP y envio de prueba |
| A23 | Utilidades de facturacion | Se agrego submenu para reimprimir y anular facturas sin codigo manual, usando permisos | A14, A17 | Reimpresion POS/carta y anulacion |
| A24 | Mejoras visuales | Se compactaron formularios, tablas, modales, dashboard, login y campos largos | A05 | Capturas antes/despues |
| A25 | Seguridad de login | Se quitaron usuario y contrasena por defecto del formulario de login | A07 | Login vacio al cargar |
| A26 | Despliegue local | Se valido el sistema con Docker Compose en ambiente local | A04, A05, A06 | Servicios backend, frontend y base activos |
| A27 | Despliegue VPS | Se preparo actualizacion desde Git, servicios systemd, Docker y Nginx | A26 | Sitio publicado y servicios activos |
| A28 | Importacion de inventario | Se preparo carga de inventario local hacia la base de datos de nube usando archivo SQL | A10, A27 | Archivo SQL, backup e importacion |
| A29 | Documentacion tecnica | Se escribieron guias de estructura, lectura de codigo, usuarios, pendientes y bitacora | Todas | Carpeta `docs` actualizada |
| A30 | Revision final | Se reviso que el proyecto tenga base para cronograma, defensa y futuras mejoras | A29 | Bitacora ampliada y lista de pendientes |

### Trabajo realizado en interfaz grafica

La interfaz grafica fue una de las partes mas visibles del proyecto. El
objetivo no fue solo crear pantallas, sino construir una experiencia que un
usuario pueda entender: iniciar sesion, navegar por modulos, registrar datos,
consultar tablas, imprimir reportes y ejecutar procesos sin perderse.

La interfaz se construyo con Vue y Vite. Se organizaron vistas por modulo,
servicios para comunicarse con el backend y rutas protegidas para controlar el
acceso. Tambien se trabajaron estilos globales para que el sistema tuviera una
apariencia uniforme en login, dashboard, ventas, inventario, usuarios, reportes
y compras.

#### Objetivos de la interfaz grafica

- Crear una entrada segura mediante login.
- Mostrar un menu lateral con los modulos principales.
- Separar cada proceso en una pantalla entendible.
- Usar formularios, tablas, botones, modales y filtros de forma consistente.
- Evitar campos demasiado grandes o desalineados.
- Permitir trabajo local en `http://localhost:5310`.
- Adaptar pantallas para escritorio y vista responsive.
- Ocultar opciones segun permisos del usuario.
- Facilitar impresion o reimpresion de documentos operativos.
- Dar una apariencia mas ordenada para presentacion academica.

#### Actividades de interfaz para cronograma

| Codigo | Actividad | Descripcion | Dependencia | Entregable |
| --- | --- | --- | --- | --- |
| GUI01 | Crear estructura frontend | Se preparo Vue/Vite con carpetas para vistas, rutas y servicios | Analisis inicial | Proyecto frontend funcional |
| GUI02 | Crear rutas de navegacion | Se definieron rutas para login, inicio, ventas, inventario, usuarios, reportes, compras y configuracion | GUI01 | `frontend/src/router` |
| GUI03 | Crear servicios API | Se crearon servicios JS para comunicarse con backend por modulo | GUI01, backend API | `frontend/src/services` |
| GUI04 | Crear login | Se diseno la pantalla de inicio de sesion con usuario y contrasena | Autenticacion backend | `LoginView.vue` |
| GUI05 | Proteger rutas | Se controlo que solo usuarios autenticados entren al sistema | GUI04 | Navegacion protegida |
| GUI06 | Crear shell principal | Se creo estructura general con sidebar, contenido principal y sesion activa | GUI05 | Layout autenticado |
| GUI07 | Crear dashboard | Se hizo una pantalla inicial para resumir acceso al sistema | GUI06 | `DashboardView.vue` |
| GUI08 | Crear productos | Se construyo pantalla para registrar, buscar y editar productos | API inventario | `ProductsView.vue` |
| GUI09 | Crear movimientos | Se construyo pantalla para ingresos, egresos, transferencias e historico | API inventario | `MovementsView.vue` |
| GUI10 | Crear produccion | Se construyo pantalla para recetas, produccion y reportes | API inventario/produccion | `ProductionView.vue` |
| GUI11 | Crear apertura de pacas | Se agrego pantalla especial para apertura, origenes y detalle | API inventario | `PacaOpeningView.vue` |
| GUI12 | Crear ventas POS | Se creo pantalla de venta con catalogo, ticket, datos comerciales y pagos | API ventas/inventario | `SalesView.vue` |
| GUI13 | Crear vales de caja | Se agrego pantalla para comprobantes de ingreso/egreso de caja | API ventas/caja | `CashVouchersView.vue` |
| GUI14 | Crear cierre de caja | Se agrego pantalla para cierre diario, desglose y movimientos | API ventas/caja | `CashCloseView.vue` |
| GUI15 | Crear utilidades de facturacion | Se agrego pantalla para buscar, reimprimir y anular facturas | API ventas/permisos | `SalesUtilitiesView.vue` |
| GUI16 | Crear usuarios y permisos | Se creo pantalla para usuarios, roles, sucursales, vendedores y accesos | API access | `UsersView.vue` |
| GUI17 | Crear configuracion empresarial | Se creo pantalla para datos del negocio, logo, tasa y parametros | API settings | `BusinessSettingsView.vue` |
| GUI18 | Crear reportes | Se creo pantalla para informes operativos y analiticos | API reports | `ReportsView.vue` |
| GUI19 | Crear compras internas | Se creo pantalla para insumos, solicitudes, cotizaciones y correos | API procurement | `ProcurementView.vue` |
| GUI20 | Mejorar estilos globales | Se ajustaron tamanos, tablas, formularios, modales, botones y responsive | Todas las vistas | `frontend/src/style.css` |

#### Pantallas creadas y funcion dentro del sistema

| Pantalla | Archivo | Funcion principal |
| --- | --- | --- |
| Login | `frontend/src/views/auth/LoginView.vue` | Permite iniciar sesion sin mostrar credenciales por defecto |
| Inicio | `frontend/src/views/dashboard/DashboardView.vue` | Presenta una entrada simple al sistema y resumen general |
| Productos | `frontend/src/views/inventory/ProductsView.vue` | Registro, busqueda, edicion y control visual de productos |
| Ingresos/Egresos | `frontend/src/views/inventory/MovementsView.vue` | Registro de movimientos y consulta de historico |
| Produccion | `frontend/src/views/inventory/ProductionView.vue` | Gestion de recetas y procesos de produccion |
| Apertura de pacas | `frontend/src/views/inventory/PacaOpeningView.vue` | Apertura, origenes, lineas y costos estimados |
| Ventas POS | `frontend/src/views/sales/SalesView.vue` | Venta, ticket, pagos, factura y recibo |
| Vales de caja | `frontend/src/views/sales/CashVouchersView.vue` | Registro de ingresos y egresos de caja |
| Cierre de caja | `frontend/src/views/sales/CashCloseView.vue` | Desglose de efectivo, resumen y cierre diario |
| Utilidades de facturacion | `frontend/src/views/sales/SalesUtilitiesView.vue` | Reimpresion y anulacion de facturas |
| Usuarios y permisos | `frontend/src/views/users/UsersView.vue` | Administracion de usuarios, roles, permisos y accesos |
| Configuracion | `frontend/src/views/settings/BusinessSettingsView.vue` | Datos del negocio, logo, tasa y parametros |
| Informes | `frontend/src/views/reports/ReportsView.vue` | Reportes operativos, analiticos y de inventario |
| Compras internas | `frontend/src/views/procurement/ProcurementView.vue` | Insumos, solicitudes, cotizaciones y notificaciones |

#### Servicios frontend creados

| Servicio | Archivo | Uso |
| --- | --- | --- |
| Autenticacion | `frontend/src/services/auth.js` | Login, sesion y usuario autenticado |
| Accesos | `frontend/src/services/access.js` | Usuarios, roles, permisos, sucursales y vendedores |
| Inventario | `frontend/src/services/inventory.js` | Productos, catalogos, saldos y movimientos |
| Ventas | `frontend/src/services/sales.js` | Facturas, pagos, caja, vales y utilidades |
| Configuracion | `frontend/src/services/settings.js` | Datos empresariales, logo, tasa y parametros |
| Reportes | `frontend/src/services/reports.js` | Consultas de informes y analisis |
| Compras | `frontend/src/services/procurement.js` | Insumos, solicitudes, cotizaciones y correos |

#### Decisiones de diseno visual

- Se uso un menu lateral para que el usuario encuentre los modulos principales.
- Se agruparon opciones por areas: Inicio, Ventas, Inventario, Administracion,
  Reportes y Compras.
- Se redujeron campos demasiado anchos en formularios como fecha, bodega y tasa
  de cambio.
- Se mejoraron modales para que los inputs no quedaran desalineados.
- Se quitaron credenciales precargadas del login por seguridad.
- Se simplifico el dashboard para que no se viera sobrecargado.
- Se agregaron colores y formas mas atractivas sin cambiar la logica.
- Se oculto la opcion de upgrade porque ya no se usaria y podia causar
  problemas operativos.
- Se mantuvieron controles conocidos: botones, tabs, tablas, modales,
  selectores, combobox y campos numericos.
- Se busco que las pantallas fueran simples de explicar para una defensa
  academica.

#### Mejoras visuales realizadas por modulo

| Modulo | Mejora aplicada | Resultado |
| --- | --- | --- |
| Login | Se quitaron usuario y contrasena por defecto | Mayor seguridad y presentacion mas limpia |
| Dashboard | Se simplifico el contenido y se ajustaron colores | Inicio mas claro y menos cargado |
| Sidebar | Se ajusto logo, ancho, colapso y opciones visibles | Navegacion mas ordenada |
| Ventas POS | Se compacto ticket, pagos, datos de factura y recibo | Flujo de venta mas practico |
| Vales de caja | Se agrego combobox de rubros para ingresos y egresos | Registro de caja mas rapido |
| Cierre de caja | Se redujeron campos de fecha, bodega y tasa | Formulario mas proporcionado |
| Productos | Se mejoraron busquedas, tablas y controles | Catalogo mas facil de usar |
| Movimientos | Se ordenaron formularios e historico | Mejor lectura de ingresos/egresos |
| Usuarios | Se mejoro UI de permisos y roles | Control de accesos mas elegante |
| Reportes | Se organizaron informes por tipo de analisis | Mejor soporte para decisiones |
| Compras internas | Se corrigio alineacion de campos en modal de solicitud | Captura de datos mas clara |
| Facturacion | Se agregaron acciones para reimprimir/anular | Herramientas administrativas visibles |

#### Componentes y patrones usados

- Formularios para crear y editar registros.
- Tablas para listar historicos, productos, usuarios, reportes y solicitudes.
- Modales para operaciones que no deben ocupar toda la pantalla.
- Combobox/selectores para catalogos como rubro, bodega, usuario o estado.
- Pestañas para separar secciones dentro de una misma pantalla.
- Botones de accion para guardar, cancelar, imprimir, buscar o anular.
- Mensajes de validacion para evitar datos incompletos.
- Tarjetas o bloques de resumen para totales e indicadores.
- Layout responsive para revisar pantallas en resoluciones pequenas.

#### Flujo visual principal del usuario

1. El usuario abre el sistema.
2. Ingresa usuario y contrasena en login.
3. El sistema valida credenciales y permisos.
4. El usuario entra al Inicio.
5. El sidebar muestra solo opciones permitidas.
6. El usuario selecciona un modulo.
7. La vista carga informacion desde la API.
8. El usuario registra, consulta, imprime o modifica datos.
9. El sistema guarda en base de datos.
10. Los reportes usan esa informacion para mostrar resultados.

#### Evidencias especificas de interfaz grafica

- Captura de `LoginView.vue` cargando campos vacios.
- Captura del dashboard simple y con colores.
- Captura del sidebar con opciones por modulo.
- Captura del POS con ticket y pagos.
- Captura del recibo o factura POS.
- Captura de vales de caja con rubros.
- Captura de cierre de caja con campos compactos.
- Captura de productos con tabla y busqueda.
- Captura de movimientos de inventario.
- Captura de usuarios y permisos.
- Captura de reportes analiticos.
- Captura del modal de solicitud de compra corregido.
- Captura de utilidades de facturacion.
- Evidencia de `npm run build` correcto.
- Evidencia de prueba local en `http://localhost:5310`.

#### Criterios de aceptacion de interfaz

| Area visual | Criterio |
| --- | --- |
| Login | Debe cargar sin usuario ni contrasena precargados |
| Navegacion | El menu debe mostrar opciones segun permisos |
| Formularios | Los campos deben estar alineados y no ocupar espacio excesivo |
| Tablas | Deben permitir lectura clara, busqueda o revision de historicos |
| Modales | Deben mostrar inputs completos sin desbordes ni desalineacion |
| Ventas | El ticket, pagos y factura deben verse en un flujo entendible |
| Caja | Fecha, bodega y tasa deben verse en tamano normal |
| Compras | La solicitud debe capturar datos sin campos montados |
| Reportes | La informacion debe estar separada por tipo de analisis |
| Responsive | La interfaz no debe romperse en pantallas pequenas |

### Trabajo realizado en base de datos

La base de datos es una parte vital del sistema porque guarda la informacion
real del negocio. Sin una base bien organizada, los modulos pueden verse bien en
pantalla, pero no tendrian control ni historial. Por eso el proyecto trabajo la
base de datos como una capa central conectada con backend, frontend, reportes,
inventario, ventas, usuarios y despliegue.

El motor usado en el ambiente Docker/VPS es PostgreSQL. El backend se conecta a
la base mediante SQLAlchemy y usa modelos para representar cada tabla. La
primera migracion formal se maneja con Alembic para usuarios y roles, y varias
tablas del sistema se crean desde `Base.metadata.create_all()` al iniciar la
aplicacion. Ademas, el arranque del backend crea datos iniciales necesarios para
que el sistema pueda usarse sin cargar todo manualmente.

#### Objetivos de la base de datos

- Guardar usuarios, roles y permisos.
- Guardar catalogos administrativos del negocio.
- Registrar productos, existencias y movimientos.
- Controlar ventas, facturas, pagos, anulaciones y caja.
- Guardar configuracion empresarial, tasa de cambio y logos.
- Registrar compras internas, insumos, solicitudes y cotizaciones.
- Guardar configuracion de notificaciones por correo.
- Servir de fuente para reportes operativos y analiticos.
- Permitir respaldo, restauracion e importacion de datos.

#### Actividades de base de datos para cronograma

| Codigo | Actividad | Descripcion | Dependencia | Entregable |
| --- | --- | --- | --- | --- |
| BD01 | Definir entidades principales | Se identificaron las entidades necesarias: usuario, rol, producto, bodega, factura, movimiento, proveedor, configuracion e insumo | Analisis del sistema | Lista de entidades |
| BD02 | Crear conexion a PostgreSQL | Se preparo la conexion del backend hacia PostgreSQL usando variables de entorno | Backend inicial | `database.py` y `.env` |
| BD03 | Crear modelos SQLAlchemy | Se representaron las tablas como clases para que el backend pueda leer y guardar datos | BD01, BD02 | Archivos en `backend/app/models` |
| BD04 | Crear migracion inicial | Se creo una migracion Alembic para usuarios y roles | BD03 | Archivo en `backend/alembic/versions` |
| BD05 | Crear tablas automaticas | Se habilito `Base.metadata.create_all()` para materializar tablas no migradas formalmente | BD03 | Tablas creadas al iniciar backend |
| BD06 | Cargar datos iniciales | Se agregaron roles, administrador, permisos, bodegas, catalogos y configuracion inicial | BD05 | Sistema usable desde primer arranque |
| BD07 | Relacionar inventario | Se conectaron productos con bodegas, saldos, ingresos, egresos y transferencias | Productos e inventario | Existencias controladas |
| BD08 | Relacionar ventas | Se conectaron facturas con items, pagos, clientes, vendedores y movimientos de inventario | Ventas POS | Factura persistente y stock afectado |
| BD09 | Relacionar permisos | Se conectaron usuarios, roles y permisos para controlar modulos | Autenticacion | Matriz de permisos funcional |
| BD10 | Crear tablas de reportes indirectos | Se usaron ventas, inventario, caja y productos como fuente de consultas analiticas | BD07, BD08 | Reportes con datos reales |
| BD11 | Incorporar compras internas | Se agregaron tablas para insumos, movimientos de insumos, solicitudes y cotizaciones | Modulo compras | Gestion de insumos |
| BD12 | Incorporar notificaciones | Se agregaron tablas para configuracion SMTP y destinatarios | Compras internas | Correos configurables |
| BD13 | Respaldar base de datos | Se preparo el uso de `pg_dump` antes de importar o actualizar datos sensibles | Despliegue VPS | Archivo `.sql` de respaldo |
| BD14 | Importar inventario local | Se preparo carga de inventario local hacia la base de datos en nube mediante SQL | BD13 | Inventario migrado sin carga manual |
| BD15 | Validar integridad | Se reviso que los movimientos afecten stock y que las relaciones funcionen | BD07, BD08 | Pruebas de consistencia |

#### Tablas por modulo

| Modulo | Tablas principales | Uso dentro del sistema |
| --- | --- | --- |
| Usuarios y seguridad | `users`, `roles`, `permissions`, `user_roles`, `role_permissions`, `user_access_profiles` | Login, roles, permisos, accesos y reglas de administrador |
| Sucursales y vendedores | `sucursales`, `vendedores` | Asociar usuarios, vendedores y bodegas a la operacion comercial |
| Catalogos de inventario | `lineas`, `segmentos`, `unidades_medida`, `marcas`, `bodegas`, `proveedores`, `ingreso_tipos`, `egreso_tipos` | Datos base para registrar productos y movimientos |
| Productos | `productos`, `saldos_productos`, `producto_combos`, `productos_recetas`, `productos_receta_lineas` | Registro de productos, saldos, combos y recetas |
| Movimientos de inventario | `ingresos_inventario`, `ingreso_items`, `egresos_inventario`, `egreso_items` | Entradas, salidas, costos, subtotales y afectacion de existencia |
| Produccion | `producciones_inventario`, `producciones_inventario_lineas` | Produccion, consumo de insumos y costo de produccion |
| Apertura de pacas | `paca_aperturas`, `paca_apertura_origenes`, `paca_apertura_lineas` | Registro de apertura, origenes, detalle y costos asignados |
| Ventas | `clientes`, `sales_invoices`, `sales_invoice_items`, `sales_payments`, `sales_sequences` | Facturas, detalle, pagos, clientes y consecutivo POS |
| Caja | `cash_closures`, `cash_vouchers`, `cash_close_movements` | Vales, ingresos/egresos de caja y cierre diario |
| Configuracion | `business_settings`, `company_environments`, `exchange_rates` | Datos del negocio, entornos y tasa de cambio |
| Compras internas | `supply_items`, `supply_movements`, `quote_requests`, `quote_request_lines`, `supplier_quotes` | Insumos, movimientos, solicitudes y cotizaciones |
| Notificaciones | `email_config`, `email_recipients` | Configuracion de correo y destinatarios |

#### Relaciones importantes

- Un usuario puede tener varios roles mediante `user_roles`.
- Un rol puede tener varios permisos mediante `role_permissions`.
- El administrador se sincroniza con todos los permisos del catalogo.
- Una bodega puede pertenecer a una sucursal.
- Un vendedor puede relacionarse con un usuario.
- Un producto puede tener saldo en una o varias bodegas.
- Un ingreso de inventario tiene varios `ingreso_items`.
- Un egreso de inventario tiene varios `egreso_items`.
- Una venta genera una factura en `sales_invoices`.
- Una factura tiene productos en `sales_invoice_items`.
- Una factura tiene pagos en `sales_payments`.
- Una factura puede generar egreso de inventario para descontar stock.
- Un cierre de caja puede incluir ventas, vales y movimientos.
- Una solicitud de compra tiene lineas de detalle.
- Una cotizacion de proveedor se relaciona con una solicitud.

#### Datos iniciales creados por el sistema

Para facilitar el uso del sistema desde cero, el arranque del backend prepara
informacion basica. Esto es importante porque evita que el usuario tenga que
llenar manualmente todos los catalogos antes de probar el ERP.

- Usuario administrador inicial.
- Rol `administrador`.
- Roles operativos como vendedor, caja, inventario y supervisor.
- Catalogo de permisos por modulo.
- Sucursal principal.
- Bodega principal.
- Lineas y segmentos base.
- Unidades de medida comunes.
- Tipos de ingreso.
- Tipos de egreso.
- Proveedores base.
- Configuracion empresarial inicial.
- Tasa/configuracion comercial base cuando aplica.

#### Reglas de integridad consideradas

- No permitir vender mas unidades que la existencia disponible.
- No permitir egresos mayores al saldo del producto en bodega.
- Mantener el administrador con todos los permisos.
- Mantener consecutivo de factura usando `sales_sequences`.
- Guardar subtotales y totales en ventas e inventario para reportes.
- Registrar moneda, tasa y conversiones cuando el flujo lo requiere.
- Conservar historial de movimientos en vez de modificar existencias sin rastro.
- Crear respaldo antes de importar inventario en la VPS.

#### Respaldo, importacion y nube

La base de datos tambien fue considerada en el despliegue. Al mover informacion
local a la VPS se definio una forma mas practica que la carga manual: generar un
archivo SQL, enviarlo mediante Git en formato seguro/transportable y luego
restaurarlo o importarlo en el servidor. Antes de aplicar cambios a datos reales
se recomendo crear un respaldo completo.

Flujo documentado:

1. Preparar inventario o datos locales.
2. Exportar a archivo SQL.
3. Comprimir/codificar si se necesita transportarlo por Git.
4. Descargar cambios en la VPS con `git pull`.
5. Generar respaldo antes de importar.
6. Importar el SQL en PostgreSQL.
7. Validar cantidades, productos y saldos.
8. Levantar servicios y probar desde la interfaz.

#### Evidencias especificas de base de datos

- Captura o salida de tablas creadas en PostgreSQL.
- Captura de `docker compose ps` mostrando el contenedor de PostgreSQL.
- Archivo de migracion Alembic inicial.
- Modelos en `backend/app/models`.
- Consulta de productos registrados.
- Consulta de saldos por bodega.
- Consulta de facturas y pagos.
- Consulta de permisos del administrador.
- Archivo `.sql` de respaldo antes de importaciones.
- Evidencia de importacion de inventario local a nube.

#### Pendientes recomendados para la base de datos

- Crear diagrama entidad-relacion actualizado.
- Formalizar todas las tablas nuevas en migraciones Alembic.
- Preparar un diccionario de datos con campo, tipo, descripcion y modulo.
- Documentar llaves primarias y llaves foraneas.
- Definir politica de respaldo diario en VPS.
- Crear procedimiento de restauracion probado.
- Revisar indices para busqueda de productos, facturas y reportes.
- Separar datos de prueba y datos reales antes de produccion.

### Detalle narrativo por modulo

#### Autenticacion y seguridad

El primer bloque funcional fue el acceso al sistema. Se necesitaba que el ERP
no quedara abierto a cualquier usuario, por eso se implemento un login con
usuario, contrasena y token JWT. Tambien se agrego la consulta del usuario
autenticado para que el frontend pudiera saber quien esta usando el sistema.

Luego se corrigio el login para no mostrar credenciales por defecto. Esta
decision fue importante porque el sistema podria ser usado en una VPS y no era
correcto que apareciera un usuario o contrasena visible al abrir la pantalla.

Resultado principal:

- Login funcional.
- Token de sesion.
- Usuario autenticado.
- Administrador con acceso completo.
- Formulario de login sin credenciales precargadas.

#### Inventario y productos

El inventario fue uno de los modulos centrales. Primero se prepararon los
catalogos necesarios para que un producto pudiera registrarse correctamente:
linea, segmento, unidad de medida, bodega, proveedor y tipos de movimiento.
Despues se agrego el registro de productos con codigos, precios y busqueda.

Con esa base se construyeron ingresos, egresos, transferencias y kardex. La
idea fue que cada movimiento afectara la existencia y que el sistema pudiera
mostrar de donde viene cada cambio de stock. Tambien se agregaron validaciones
para evitar egresos mayores a la existencia disponible.

Resultado principal:

- Productos registrados.
- Saldos por bodega.
- Ingresos y egresos con validacion.
- Transferencias entre bodegas.
- Kardex para seguimiento.
- Reportes de movimientos.

#### Produccion

El modulo de produccion se agrego para representar procesos donde se consumen
insumos o productos y se genera una salida. Se trabajaron recetas, apertura de
produccion, ejecucion y reporte. Este modulo depende directamente de inventario
porque necesita validar existencias antes de consumir materiales.

Resultado principal:

- Recetas de produccion.
- Apertura y ejecucion de produccion.
- Consumo de inventario.
- Reporte de produccion.

#### Ventas y facturacion

Ventas fue trabajado como un punto de venta. Primero se construyo la interfaz
para buscar productos, agregarlos a un ticket y seleccionar datos comerciales.
Luego se incorporo el flujo de pagos, factura, recibo y descuento de inventario.

Tambien se mejoro el diseno para que la pantalla fuera mas practica: paneles
compactos, resumen del ticket, recibo POS y validaciones de stock. Despues se
agregaron utilidades de facturacion para anular y reimprimir facturas. La
autorizacion de estas opciones se maneja por permisos, no por un codigo manual.

Resultado principal:

- Pantalla POS.
- Busqueda de productos.
- Ticket de venta.
- Pagos.
- Factura y recibo.
- Descuento de inventario.
- Reimpresion POS/carta.
- Anulacion controlada por permisos.

#### Configuracion empresarial

Este modulo permite adaptar el sistema al negocio. Se agregaron datos generales,
logo, politicas, entorno y tasa de cambio. Fue importante porque varias pantallas
dependen de esta informacion para mostrar identidad visual, moneda y parametros
de operacion.

Resultado principal:

- Datos del negocio.
- Logo del comercio.
- Politicas comerciales.
- Tasa de cambio.
- Configuracion reutilizada por otros modulos.

#### Usuarios, roles y permisos

El modulo de usuarios se reforzo para que el sistema no dependa solo de iniciar
sesion. Se agregaron permisos por modulo y funcionalidad. Esto permite ocultar o
mostrar opciones segun el rol del usuario. Tambien se dejo una regla clara:
todo nuevo modulo u opcion debe agregarse al sistema de permisos.

Resultado principal:

- Usuarios administrables.
- Roles y permisos.
- Control de opciones por modulo.
- Administrador con acceso total siempre.
- Base para seguridad funcional del sistema.

#### Informes y reportes

Se agrego un modulo de informes para apoyar la toma de decisiones. No solo se
consideraron reportes basicos, sino tambien reportes de analisis como productos
estancados, productos de mayor movimiento y revision de inventario.

Resultado principal:

- Reportes operativos.
- Reportes analiticos.
- Informacion para gerencia.
- Base para exportaciones o analisis externos.

#### Compras internas y cotizaciones

Se creo un modulo de compras internas que no esta orientado a mercaderia para
venta, sino a insumos que la empresa necesita controlar. Por ejemplo: limpieza,
papeleria, mantenimiento, materiales de oficina u otros recursos internos.

Tambien se incorporo el flujo de solicitudes y cotizaciones. Se considero la
opcion de agregar destinatarios y enviar notificaciones por correo, porque en un
proceso real de compras es necesario comunicar solicitudes y aprobaciones.

Resultado principal:

- Inventario de insumos.
- Solicitudes de compra.
- Cotizaciones.
- Proveedores o contactos.
- Base para envio de correos.

#### Despliegue y actualizacion

El proyecto no se dejo solo como ambiente local. Se trabajo el despliegue en
VPS, actualizacion desde Git, servicios de sistema, Docker Compose y Nginx. En
este proceso se resolvieron problemas reales como puertos ocupados, permisos de
Docker, configuracion de Nginx, errores 502 y variables de entorno.

Resultado principal:

- Proyecto versionado en GitHub.
- Actualizacion desde VPS con `git pull`.
- Servicios systemd.
- Docker Compose en servidor.
- Nginx como proxy.
- Correcciones de puertos y permisos.

### Dependencias principales para Gantt

| Actividad | No debe iniciar antes de | Motivo |
| --- | --- | --- |
| Ventas POS | Productos e inventario | Ventas necesita productos y existencias |
| Facturacion | Ventas POS | La factura nace del ticket de venta |
| Descuento de stock | Facturacion e inventario | Se requiere una venta confirmada y stock disponible |
| Reportes de ventas | Facturacion | Los reportes necesitan facturas guardadas |
| Productos estancados | Inventario y ventas | Se comparan existencias contra movimiento |
| Permisos por modulo | Autenticacion y rutas | Se necesita saber quien entra y que opciones existen |
| Compras internas | Usuarios y configuracion | Se requiere control de acceso y datos empresariales |
| Correos | Compras internas y configuracion SMTP | El envio depende de solicitudes y credenciales de correo |
| Despliegue VPS | Sistema local estable | Primero debe funcionar localmente |
| Importacion de inventario | Base de datos VPS activa | Se necesita destino estable antes de cargar datos |

### Criterios de aceptacion por area

| Area | Criterio de aceptacion |
| --- | --- |
| Login | El usuario puede iniciar sesion con credenciales validas y el formulario carga vacio |
| Usuarios | El administrador ve todas las opciones y puede gestionar permisos |
| Productos | Un producto puede crearse, editarse, buscarse y asociarse a saldos |
| Inventario | Un ingreso aumenta existencia y un egreso no permite exceder stock |
| Ventas | Una venta registra factura, detalle, pagos y afecta inventario |
| Reportes | El usuario puede consultar informacion filtrada y util para decision |
| Compras | Una solicitud puede registrarse con insumos y datos de cotizacion |
| Correos | El sistema puede preparar destinatarios y enviar notificaciones configuradas |
| Facturacion | Una factura puede reimprimirse o anularse segun permisos |
| Despliegue | El sistema puede levantarse localmente y actualizarse en VPS desde Git |
| Documentacion | La bitacora y guias explican el proceso, estructura y pendientes |

### Riesgos encontrados y solucion aplicada

| Riesgo o problema | Impacto | Solucion aplicada o recomendada |
| --- | --- | --- |
| Puertos ocupados en VPS | El backend no podia iniciar | Cambiar puerto publicado y ajustar Nginx |
| Error 502 en Nginx | La nube mostraba gateway error | Revisar proxy, backend activo y rutas configuradas |
| Permiso denegado en Docker | No se podian ver o levantar contenedores sin `sudo` | Ejecutar comandos con `sudo` o ajustar grupo Docker |
| Repositorio con propiedad dudosa | El servicio de actualizacion fallaba con Git | Agregar `safe.directory` para el repo |
| Password incorrecto de PostgreSQL | Backend no conectaba a base de datos | Revisar `.env`, usuario y password del volumen |
| Login con datos por defecto | Riesgo de seguridad | Quitar valores precargados del formulario |
| Modulos nuevos sin permisos | Riesgo de acceso no controlado | Regla: toda opcion nueva debe registrarse en permisos |
| Campos visuales desalineados | Mala experiencia de usuario | Ajustar tamanos, grillas, modales y estilos |
| Inventario manual en nube | Mucho trabajo operativo | Importacion por archivo SQL versionado y carga controlada |

### Evidencias que pueden adjuntarse al informe

- Captura del login sin credenciales por defecto.
- Captura del dashboard simplificado.
- Captura de productos e inventario.
- Captura de ingresos/egresos y reporte.
- Captura de ventas POS con ticket.
- Captura de recibo o factura.
- Captura de usuarios y permisos.
- Captura del modulo de informes.
- Captura de compras internas.
- Captura de utilidades de facturacion.
- Captura de la aplicacion levantada localmente.
- Captura del sitio funcionando en VPS.
- Salida de `docker compose ps`.
- Salida de `npm run build`.
- Historial de commits de Git.

### Actividades pendientes organizadas para siguiente etapa

| Prioridad | Actividad | Objetivo |
| --- | --- | --- |
| Alta | Revisar matriz completa de permisos | Confirmar que cada modulo y boton sensible tenga permiso |
| Alta | Validar anulacion de facturas con datos reales | Evitar inconsistencias contables o de inventario |
| Alta | Validar importacion de inventario en VPS | Asegurar que datos locales y nube queden sincronizados |
| Media | Completar manual de usuario | Facilitar capacitacion y defensa |
| Media | Crear plan formal de pruebas | Documentar casos exitosos y errores corregidos |
| Media | Preparar diagramas | Arquitectura, base de datos y casos de uso |
| Media | Revisar reportes con usuarios | Confirmar que los informes realmente ayuden a decidir |
| Baja | Mejoras visuales adicionales | Pulir experiencia sin cambiar logica principal |
| Baja | Limpieza de textos tecnicos visibles | Dejar lenguaje mas claro para usuarios finales |

### Nota de aprendizaje del equipo

Durante el desarrollo se aprendio que un sistema empresarial no se construye en
una sola pantalla ni en un solo modulo. Cada cambio afecta otras partes: una
venta afecta inventario, un usuario necesita permisos, un reporte necesita datos
confiables y un despliegue necesita variables correctas. Por eso se documento
el proceso paso a paso, para demostrar no solo el resultado final, sino tambien
el camino seguido para llegar a un sistema funcional.

Tambien se aprendio que trabajar primero en local ayuda a corregir errores antes
de afectar la nube. Despues de validar localmente, los cambios se enviaron por
Git y se actualizaron en la VPS. Esta forma de trabajo permite conservar un
historial, regresar a versiones anteriores si fuera necesario y explicar mejor
como evoluciono el proyecto.
