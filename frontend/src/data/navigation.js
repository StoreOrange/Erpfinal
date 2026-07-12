// Lista simple de accesos usados por el dashboard y otras partes visuales.
// Si se agrega un modulo nuevo, conviene registrarlo aqui para mantener
// la navegacion del sistema en un solo lugar.
export const appNavigation = [
  {
    label: "Inicio",
    icon: "bi-speedometer2",
    route: "/app/dashboard",
  },
  {
    label: "Usuarios",
    icon: "bi-people-fill",
    route: "/app/users",
  },
  {
    label: "Productos",
    icon: "bi-box-seam",
    route: "/app/products",
  },
  {
    label: "Inventario",
    icon: "bi-archive",
    route: "/app/inventory/movements",
  },
  {
    label: "Apertura de Pacas",
    icon: "bi-box-arrow-in-down",
    route: "/app/inventory/paca-opening",
  },
  {
    label: "Ventas y Facturacion",
    icon: "bi-cart-check",
    route: "/app/sales",
  },
  {
    label: "Vales de Caja",
    icon: "bi-receipt",
    route: "/app/sales/cash-vouchers",
  },
  {
    label: "Cierre de Caja Diario",
    icon: "bi-cash-coin",
    route: "/app/sales/cash-close",
  },
  {
    label: "Informes",
    icon: "bi-graph-up-arrow",
    route: "/app/reports",
  },
  {
    label: "Compras Operativas",
    icon: "bi-bag-check",
    route: "/app/procurement",
  },
  {
    label: "Datos y Configuraciones",
    icon: "bi-buildings",
    route: "/app/settings/business",
  },
];
