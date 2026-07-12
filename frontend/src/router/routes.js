import AppShell from "../layouts/AppShell.vue";
import DashboardView from "../views/dashboard/DashboardView.vue";
import LoginView from "../views/auth/LoginView.vue";
import ProductsView from "../views/inventory/ProductsView.vue";
import MovementsView from "../views/inventory/MovementsView.vue";
import PacaOpeningView from "../views/inventory/PacaOpeningView.vue";
import ProductionView from "../views/inventory/ProductionView.vue";
import SalesView from "../views/sales/SalesView.vue";
import CashCloseView from "../views/sales/CashCloseView.vue";
import CashVouchersView from "../views/sales/CashVouchersView.vue";
import SalesUtilitiesView from "../views/sales/SalesUtilitiesView.vue";
import BusinessSettingsView from "../views/settings/BusinessSettingsView.vue";
import UsersView from "../views/users/UsersView.vue";
import ReportsView from "../views/reports/ReportsView.vue";
import ProcurementView from "../views/procurement/ProcurementView.vue";

// Rutas principales del frontend.
// Cada objeto representa una pantalla disponible en la aplicacion.
// Las pantallas protegidas viven dentro de /app y usan el layout AppShell.
export const routes = [
  {
    path: "/",
    redirect: "/app/dashboard",
  },
  {
    path: "/login",
    name: "login",
    component: LoginView,
    meta: { guestOnly: true },
  },
  {
    path: "/app",
    component: AppShell,
    meta: { requiresAuth: true },
    children: [
      {
        path: "dashboard",
        name: "dashboard",
        component: DashboardView,
      },
      {
        path: "users",
        name: "users",
        component: UsersView,
      },
      {
        path: "products",
        name: "products",
        component: ProductsView,
      },
      {
        path: "inventory/movements",
        name: "inventory-movements",
        component: MovementsView,
      },
      {
        path: "inventory/production",
        name: "inventory-production",
        component: ProductionView,
      },
      {
        path: "inventory/paca-opening",
        name: "inventory-paca-opening",
        component: PacaOpeningView,
      },
      {
        path: "sales",
        name: "sales",
        component: SalesView,
      },
      {
        path: "sales/cash-close",
        name: "cash-close",
        component: CashCloseView,
      },
      {
        path: "sales/cash-vouchers",
        name: "cash-vouchers",
        component: CashVouchersView,
      },
      {
        path: "sales/utilities",
        name: "sales-utilities",
        component: SalesUtilitiesView,
      },
      {
        path: "reports",
        name: "reports",
        component: ReportsView,
      },
      {
        path: "procurement",
        name: "procurement",
        component: ProcurementView,
      },
      {
        path: "settings/business",
        name: "business-settings",
        component: BusinessSettingsView,
      },
      {
        path: "settings/upgrade",
        redirect: "/app/dashboard",
      },
    ],
  },
  {
    path: "/home",
    redirect: "/app/dashboard",
  },
];
