<!--
  Dashboard principal.
  Hecho por Carlos.
  Colaboracion academica: Oded Garcia y Carlos Ramirez.
  Nota: esta pantalla debe ser simple, clara y rapida para entrar a modulos.
-->
<template>
  <section class="page-section dashboard-simple-page">
    <header class="dashboard-simple-header">
      <div class="dashboard-header-accent"></div>
      <div>
        <p class="page-kicker">Inicio</p>
        <h1 class="page-title">Panel principal</h1>
        <p class="dashboard-simple-subtitle">Resumen rapido y accesos principales del sistema.</p>
      </div>
      <div class="dashboard-simple-session">
        <span>{{ todayLabel }}</span>
        <strong>{{ currentRole }}</strong>
      </div>
    </header>

    <section class="dashboard-simple-kpis">
      <article class="dashboard-simple-kpi kpi-products">
        <div class="dashboard-kpi-icon"><i class="bi bi-box-seam"></i></div>
        <div>
          <span>Productos</span>
          <Skeleton v-if="loading" width="4rem" height="1.4rem" />
          <strong v-else>{{ totals.products }}</strong>
          <small>Registrados en catalogo</small>
        </div>
      </article>
      <article class="dashboard-simple-kpi kpi-income">
        <div class="dashboard-kpi-icon"><i class="bi bi-arrow-down-circle"></i></div>
        <div>
          <span>Ingresos</span>
          <Skeleton v-if="loading" width="4rem" height="1.4rem" />
          <strong v-else>{{ totals.ingresos }}</strong>
          <small>Movimientos de entrada</small>
        </div>
      </article>
      <article class="dashboard-simple-kpi kpi-outcome">
        <div class="dashboard-kpi-icon"><i class="bi bi-arrow-up-circle"></i></div>
        <div>
          <span>Egresos</span>
          <Skeleton v-if="loading" width="4rem" height="1.4rem" />
          <strong v-else>{{ totals.egresos }}</strong>
          <small>Movimientos de salida</small>
        </div>
      </article>
    </section>

    <section class="panel-card dashboard-simple-actions">
      <div class="dashboard-simple-section-head">
        <div>
          <span class="products-section-kicker">Accesos</span>
          <h2>Modulos principales</h2>
        </div>
      </div>
      <div class="dashboard-simple-links">
        <RouterLink
          v-for="item in mainLinks"
          :key="item.route"
          :to="item.route"
          class="dashboard-simple-link"
          :class="linkClass(item.route)"
        >
          <i class="bi" :class="item.icon"></i>
          <span>{{ item.label }}</span>
        </RouterLink>
      </div>
    </section>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { RouterLink } from "vue-router";
import Skeleton from "primevue/skeleton";

import { appNavigation } from "../../data/navigation";
import { readStoredUser } from "../../services/auth";
import { fetchEgresos, fetchIngresos, fetchProducts } from "../../services/inventory";

const mainRoutes = new Set([
  "/app/sales",
  "/app/products",
  "/app/inventory/movements",
  "/app/reports",
  "/app/procurement",
  "/app/users",
]);
const mainLinks = appNavigation.filter((item) => mainRoutes.has(item.route));
const currentUser = readStoredUser();
const loading = ref(true);
const totals = reactive({
  products: 0,
  ingresos: 0,
  egresos: 0,
});

const todayLabel = computed(() => {
  return new Intl.DateTimeFormat("es-NI", {
    day: "2-digit",
    month: "long",
    year: "numeric",
  }).format(new Date());
});

const currentRole = computed(() => {
  const roles = currentUser?.roles || [];
  return roles.length ? roles[0].name : "Sesion principal";
});

onMounted(async () => {
  loading.value = true;
  try {
    const [products, ingresos, egresos] = await Promise.all([
      fetchProducts(),
      fetchIngresos(),
      fetchEgresos(),
    ]);
    totals.products = products.length;
    totals.ingresos = ingresos.length;
    totals.egresos = egresos.length;
  } catch {
    totals.products = 0;
    totals.ingresos = 0;
    totals.egresos = 0;
  } finally {
    loading.value = false;
  }
});

function linkClass(route) {
  const map = {
    "/app/sales": "link-sales",
    "/app/products": "link-products",
    "/app/inventory/movements": "link-inventory",
    "/app/reports": "link-reports",
    "/app/procurement": "link-procurement",
    "/app/users": "link-users",
  };
  return map[route] || "";
}
</script>

<style scoped>
.dashboard-simple-page {
  display: grid;
  gap: 1rem;
}

.dashboard-simple-header {
  align-items: center;
  background:
    linear-gradient(135deg, rgba(15, 23, 42, 0.96), rgba(30, 64, 175, 0.9)),
    radial-gradient(circle at 82% 20%, rgba(45, 212, 191, 0.25), transparent 28%);
  border: 1px solid rgba(255, 255, 255, 0.16);
  border-radius: 12px;
  color: #fff;
  display: flex;
  gap: 1rem;
  justify-content: space-between;
  overflow: hidden;
  padding: 1.2rem;
  position: relative;
}

.dashboard-header-accent {
  background: linear-gradient(180deg, #2dd4bf, #f59e0b);
  border-radius: 999px;
  bottom: 1rem;
  left: 0.85rem;
  position: absolute;
  top: 1rem;
  width: 4px;
}

.dashboard-simple-header > div:not(.dashboard-header-accent) {
  position: relative;
  z-index: 1;
}

.dashboard-simple-header .page-kicker,
.dashboard-simple-header .page-title,
.dashboard-simple-header .dashboard-simple-subtitle {
  color: #fff;
}

.dashboard-simple-subtitle {
  opacity: 0.78;
  margin: 0.35rem 0 0;
}

.dashboard-simple-session {
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.22);
  border-radius: 8px;
  display: grid;
  gap: 0.2rem;
  min-width: 190px;
  padding: 0.75rem 0.9rem;
  text-align: right;
}

.dashboard-simple-session span,
.dashboard-simple-kpi span {
  color: var(--erp-text-soft);
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0;
  text-transform: uppercase;
}

.dashboard-simple-session strong {
  color: #fff;
  font-size: 0.95rem;
}

.dashboard-simple-kpis {
  display: grid;
  gap: 0.85rem;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.dashboard-simple-kpi {
  align-items: center;
  background: #fff;
  border: 1px solid rgba(148, 163, 184, 0.26);
  border-radius: 12px;
  box-shadow: 0 14px 34px rgba(15, 23, 42, 0.06);
  display: grid;
  gap: 0.85rem;
  grid-template-columns: auto 1fr;
  min-height: 112px;
  overflow: hidden;
  padding: 1rem;
  position: relative;
}

.dashboard-simple-kpi::before {
  border-radius: 999px;
  content: "";
  height: 82px;
  opacity: 0.12;
  position: absolute;
  right: -22px;
  top: -28px;
  width: 82px;
}

.dashboard-kpi-icon {
  align-items: center;
  border-radius: 10px;
  color: #fff;
  display: inline-flex;
  font-size: 1.25rem;
  height: 2.75rem;
  justify-content: center;
  width: 2.75rem;
}

.kpi-products .dashboard-kpi-icon,
.kpi-products::before {
  background: #2563eb;
}

.kpi-income .dashboard-kpi-icon,
.kpi-income::before {
  background: #059669;
}

.kpi-outcome .dashboard-kpi-icon,
.kpi-outcome::before {
  background: #d97706;
}

.dashboard-simple-kpi strong {
  color: var(--erp-text);
  font-size: 1.8rem;
  line-height: 1.1;
}

.dashboard-simple-kpi small {
  color: var(--erp-text-soft);
}

.dashboard-simple-section-head {
  align-items: center;
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.85rem;
}

.dashboard-simple-section-head h2 {
  font-size: 1.05rem;
  margin: 0.15rem 0 0;
}

.dashboard-simple-actions {
  background: linear-gradient(180deg, #fff, #f8fafc);
  border-color: rgba(148, 163, 184, 0.28);
  border-radius: 12px;
}

.dashboard-simple-links {
  display: grid;
  gap: 0.65rem;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.dashboard-simple-link {
  align-items: center;
  background: #fff;
  border: 1px solid rgba(148, 163, 184, 0.35);
  border-radius: 8px;
  color: var(--erp-text);
  display: flex;
  gap: 0.65rem;
  min-height: 3.1rem;
  padding: 0.75rem;
  text-decoration: none;
  transition: border-color 0.15s ease, color 0.15s ease, transform 0.15s ease, box-shadow 0.15s ease;
}

.dashboard-simple-link:hover {
  border-color: var(--erp-primary);
  color: var(--erp-primary);
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
  transform: translateY(-1px);
}

.dashboard-simple-link i {
  align-items: center;
  background: rgba(15, 23, 42, 0.06);
  border-radius: 8px;
  display: inline-flex;
  flex: 0 0 2rem;
  height: 2rem;
  justify-content: center;
}

.dashboard-simple-link span {
  font-weight: 800;
}

.dashboard-simple-link.link-sales i {
  background: rgba(37, 99, 235, 0.12);
  color: #2563eb;
}

.dashboard-simple-link.link-products i {
  background: rgba(5, 150, 105, 0.12);
  color: #059669;
}

.dashboard-simple-link.link-inventory i {
  background: rgba(217, 119, 6, 0.14);
  color: #b45309;
}

.dashboard-simple-link.link-reports i {
  background: rgba(124, 58, 237, 0.12);
  color: #7c3aed;
}

.dashboard-simple-link.link-procurement i {
  background: rgba(8, 145, 178, 0.12);
  color: #0891b2;
}

.dashboard-simple-link.link-users i {
  background: rgba(225, 29, 72, 0.12);
  color: #e11d48;
}

@media (max-width: 900px) {
  .dashboard-simple-header {
    align-items: stretch;
    flex-direction: column;
  }

  .dashboard-simple-session {
    text-align: left;
  }

  .dashboard-simple-kpis,
  .dashboard-simple-links {
    grid-template-columns: 1fr;
  }
}
</style>
