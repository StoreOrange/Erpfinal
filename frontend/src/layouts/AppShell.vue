<template>
  <div :class="['app-shell erp-enterprise-shell', { 'sidebar-collapsed': collapsed }]">
    <aside :class="['app-sidebar', { collapsed }]" aria-label="Navegacion principal">
      <div class="sidebar-top">
        <div class="brand-wrap" v-if="!collapsed">
          <div class="brand-logo-shell" v-if="businessSettings.logo_sidebar">
            <img :src="buildAssetUrl(businessSettings.logo_sidebar)" :alt="businessLabel" />
          </div>
          <p class="brand-kicker">Sistema empresarial</p>
          <h1 class="brand-name">{{ businessLabel }}</h1>
          <p v-if="businessSettings.sidebar_subtitle" class="brand-caption">{{ businessSettings.sidebar_subtitle }}</p>
        </div>
      </div>

      <div class="sidebar-toggle-row">
        <button
          class="sidebar-toggle"
          type="button"
          :aria-label="collapsed ? 'Expandir menu lateral' : 'Contraer menu lateral'"
          :aria-expanded="!collapsed"
          @click="collapsed = !collapsed"
        >
          <i class="bi" :class="collapsed ? 'bi-chevron-double-right' : 'bi-chevron-double-left'"></i>
        </button>
      </div>

      <div class="sidebar-menu-area">
        <p v-if="!collapsed" class="sidebar-section-title">Aplicaciones</p>
        <PanelMenu v-if="!collapsed" :model="panelNavigation" class="enterprise-panel-menu" />
        <nav v-else class="sidebar-nav sidebar-nav-collapsed">
          <RouterLink
            v-for="item in flatNavigation"
            :key="item.route"
            :to="item.route"
            class="nav-link-item"
            active-class="is-active"
            :title="collapsed ? item.label : ''"
          >
            <i class="bi" :class="item.icon"></i>
            <span v-if="!collapsed" class="nav-label">{{ item.label }}</span>
          </RouterLink>
        </nav>
      </div>

      <div class="sidebar-bottom">
        <Button class="sidebar-logout-button" severity="secondary" variant="outlined" @click="logout">
          <i class="bi bi-box-arrow-right"></i>
          <span v-if="!collapsed">Salir</span>
        </Button>

        <div v-if="!collapsed" class="sidebar-footer">
          <div class="sidebar-footer-card">
            <div class="sidebar-user-head">
              <div class="sidebar-user-copy">
                <span class="sidebar-user-kicker">Sesion activa</span>
                <strong>{{ currentUser?.full_name || "Sin sesion" }}</strong>
              </div>
              <div class="sidebar-user-status sidebar-user-status-inline" :class="{ online: Boolean(currentUser?.is_active) }">
                <span class="status-dot"></span>
                <span>{{ currentUser?.is_active ? "Activo" : "Inactivo" }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </aside>

    <div class="app-main">
      <header class="enterprise-topbar">
        <div class="enterprise-topbar-left">
          <Button
            class="enterprise-mobile-menu"
            icon="bi bi-list"
            severity="secondary"
            variant="text"
            rounded
            aria-label="Abrir menu de aplicaciones"
            @click="mobileMenuOpen = true"
          />
          <div>
            <Breadcrumb :home="breadcrumbHome" :model="breadcrumbItems" class="enterprise-breadcrumb" />
            <h2>{{ currentPageTitle }}</h2>
          </div>
        </div>
        <div class="enterprise-topbar-actions">
          <Badge :value="totalsBadge" severity="info" />
          <Avatar :label="avatarLabel" shape="circle" class="enterprise-avatar" />
        </div>
      </header>
      <div class="app-content">
        <RouterView />
      </div>
    </div>

    <Drawer v-model:visible="mobileMenuOpen" header="Aplicaciones" class="enterprise-mobile-drawer">
      <PanelMenu :model="panelNavigation" class="enterprise-panel-menu" />
    </Drawer>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { RouterLink, RouterView, useRoute, useRouter } from "vue-router";
import Avatar from "primevue/avatar";
import Badge from "primevue/badge";
import Breadcrumb from "primevue/breadcrumb";
import Button from "primevue/button";
import Drawer from "primevue/drawer";
import PanelMenu from "primevue/panelmenu";

import { appNavigation as navigation } from "../data/navigation";
import { clearSession, fetchCurrentUser, readStoredUser } from "../services/auth";
import {
  applyBusinessBranding,
  buildAssetUrl,
  fetchPublicBusinessSettings,
  readStoredBusinessSettings,
} from "../services/settings";

const collapsed = ref(localStorage.getItem("sidebarCollapsed") === "true");
const mobileMenuOpen = ref(false);
const currentUser = ref(readStoredUser());
const businessSettings = ref(
  readStoredBusinessSettings() || {
    business_name: "Orange Tec",
    trade_name: "Orange Tec",
    sidebar_subtitle: "Sistema empresarial",
    logo_sidebar: "",
    logo_favicon: "",
  },
);
const router = useRouter();
const route = useRoute();

const businessLabel = computed(
  () => businessSettings.value?.trade_name || businessSettings.value?.business_name || "Orange Tec",
);
const avatarLabel = computed(() => (currentUser.value?.full_name || "S").slice(0, 1).toUpperCase());
const totalsBadge = computed(() => currentUser.value?.is_active ? "Activo" : "Sesion");
const flatNavigation = computed(() => navigation);
const currentPageTitle = computed(() => routeLabelMap[route.name] || "Sistema empresarial");
const breadcrumbItems = computed(() => {
  const current = currentPageTitle.value;
  if (route.name === "dashboard") return [{ label: "Dashboard" }];
  const section = route.path.includes("/inventory")
    ? "Inventario"
    : route.path.includes("/settings")
      ? "Datos"
      : route.path.includes("/sales")
        ? "Ventas y Facturacion"
        : route.path.includes("/reports")
          ? "Informes"
          : route.path.includes("/procurement")
            ? "Compras"
        : route.path.includes("/users")
          ? "Seguridad"
          : "Aplicaciones";
  return [{ label: section }, { label: current }];
});
const breadcrumbHome = computed(() => ({
  icon: "bi bi-house-door",
  command: () => goTo("/app/dashboard"),
}));
const panelNavigation = computed(() => [
  {
    label: "Inicio",
    icon: "bi bi-speedometer2",
    command: () => goTo("/app/dashboard"),
  },
  {
    label: "Ventas y Facturacion",
    icon: "bi bi-shop",
    items: [
      { label: "Ventas y Facturacion", icon: "bi bi-cart-check", command: () => goTo("/app/sales") },
      { label: "Vales de Caja", icon: "bi bi-receipt", command: () => goTo("/app/sales/cash-vouchers") },
      { label: "Cierre de caja diario", icon: "bi bi-cash-coin", command: () => goTo("/app/sales/cash-close") },
      { label: "Utilidades de facturacion", icon: "bi bi-tools", command: () => goTo("/app/sales/utilities") },
    ],
  },
  {
    label: "Inventario",
    icon: "bi bi-boxes",
    items: [
      { label: "Productos", icon: "bi bi-box-seam", command: () => goTo("/app/products") },
      { label: "Ingresos y egresos", icon: "bi bi-arrow-left-right", command: () => goTo("/app/inventory/movements") },
      { label: "Apertura de pacas", icon: "bi bi-box-arrow-in-down", command: () => goTo("/app/inventory/paca-opening") },
    ],
  },
  {
    label: "Informes",
    icon: "bi bi-graph-up-arrow",
    items: [
      { label: "Panel de informes", icon: "bi bi-clipboard-data", command: () => goTo("/app/reports") },
    ],
  },
  {
    label: "Compras",
    icon: "bi bi-bag-check",
    items: [
      { label: "Compras operativas", icon: "bi bi-clipboard-check", command: () => goTo("/app/procurement") },
    ],
  },
  {
    label: "Administracion",
    icon: "bi bi-building-gear",
    items: [
      { label: "Usuarios", icon: "bi bi-people-fill", command: () => goTo("/app/users") },
      { label: "Datos y configuraciones", icon: "bi bi-sliders", command: () => goTo("/app/settings/business") },
    ],
  },
]);
const routeLabelMap = {
  dashboard: "Panel principal",
  users: "Usuarios y accesos",
  products: "Productos",
  "inventory-movements": "Ingresos y egresos",
  "inventory-paca-opening": "Apertura de pacas",
  "inventory-production": "Produccion",
  sales: "Ventas y Facturacion",
  "cash-vouchers": "Vales de Caja",
  "cash-close": "Cierre de caja diario",
  "sales-utilities": "Utilidades de facturacion",
  reports: "Informes",
  procurement: "Compras operativas",
  "business-settings": "Datos y configuraciones",
};

function goTo(path) {
  mobileMenuOpen.value = false;
  router.push(path);
}

async function hydrateUser() {
  if (!localStorage.getItem("token")) {
    currentUser.value = null;
    return;
  }

  try {
    currentUser.value = await fetchCurrentUser();
    localStorage.setItem("currentUser", JSON.stringify(currentUser.value));
  } catch {
    clearSession();
    currentUser.value = null;
    router.push("/login");
  }
}

async function hydrateBusinessSettings() {
  try {
    businessSettings.value = await fetchPublicBusinessSettings();
    applyBusinessBranding(businessSettings.value);
  } catch {
    // Keep shell usable even if branding config is not available.
  }
}

function logout() {
  clearSession();
  currentUser.value = null;
  router.push("/login");
}

onMounted(() => {
  hydrateBusinessSettings();
  hydrateUser();
  window.addEventListener("business-settings-updated", syncBusinessSettings);
});

watch(collapsed, (value) => {
  localStorage.setItem("sidebarCollapsed", value ? "true" : "false");
});

function syncBusinessSettings(event) {
  businessSettings.value = event.detail || businessSettings.value;
}

onBeforeUnmount(() => {
  window.removeEventListener("business-settings-updated", syncBusinessSettings);
});
</script>
