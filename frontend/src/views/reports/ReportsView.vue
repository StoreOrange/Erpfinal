<!--
  Modulo de informes.
  Hecho por Carlos.
  Colaboracion academica: Oded Garcia y Carlos Ramirez.
  Recordatorio: los informes deben consultar datos, no modificar operaciones.
-->
<template>
  <section class="page-section reports-page">
    <header class="module-hero reports-hero">
      <div class="module-hero-copy">
        <p class="page-kicker">Informes</p>
        <h1 class="page-title">Panel de reportes operativos</h1>
        <p class="panel-text">
          Consulta ventas, productos vendidos, utilidad, saldos de inventario, kardex y movimientos de caja.
        </p>
      </div>
      <div class="module-hero-meta">
        <div class="module-meta-box">
          <span>Ventas C$</span>
          <strong>{{ formatMoney(summary.sales.total_cs) }}</strong>
        </div>
        <div class="module-meta-box">
          <span>Facturas</span>
          <strong>{{ summary.sales.invoice_count }}</strong>
        </div>
        <div class="module-meta-box">
          <span>Inventario C$</span>
          <strong>{{ formatMoney(summary.inventory.valor_costo_cs) }}</strong>
        </div>
      </div>
    </header>

    <section class="panel-card reports-filter-panel">
      <div class="reports-filter-grid">
        <label class="field-group">
          <span>Desde</span>
          <InputText v-model="filters.start_date" type="date" />
        </label>
        <label class="field-group">
          <span>Hasta</span>
          <InputText v-model="filters.end_date" type="date" />
        </label>
        <label class="field-group">
          <span>Bodega</span>
          <Select v-model="filters.bodega_id" :options="bodegas" option-label="name" option-value="id" show-clear filter placeholder="Todas" />
        </label>
        <label class="field-group">
          <span>Producto para kardex</span>
          <Select v-model="filters.product_id" :options="products" option-label="descripcion" option-value="id" show-clear filter placeholder="Todos" />
        </label>
        <label class="field-group">
          <span>Dias sin movimiento</span>
          <InputText v-model.number="filters.days_without_movement" type="number" min="1" />
        </label>
        <label class="field-group">
          <span>Stock maximo bajo</span>
          <InputText v-model.number="filters.max_stock" type="number" min="0" />
        </label>
        <div class="reports-actions">
          <Button icon="bi bi-arrow-clockwise" label="Actualizar" :loading="loading" @click="loadActiveReport" />
          <Button icon="bi bi-printer" label="Imprimir" severity="secondary" variant="outlined" @click="printReport" />
          <Button icon="bi bi-filetype-csv" label="CSV" severity="secondary" variant="outlined" @click="exportCsv" />
        </div>
      </div>
    </section>

    <div class="reports-tabs">
      <button v-for="tab in reportTabs" :key="tab.key" type="button" :class="{ active: activeReport === tab.key }" @click="selectReport(tab.key)">
        <i class="bi" :class="tab.icon"></i>
        <span>{{ tab.label }}</span>
      </button>
    </div>

    <section class="reports-kpi-grid">
      <article class="reports-kpi">
        <span>Ticket promedio</span>
        <strong>C$ {{ formatMoney(summary.sales.average_ticket_cs) }}</strong>
      </article>
      <article class="reports-kpi">
        <span>Ingresos caja</span>
        <strong>C$ {{ formatMoney(summary.cash_vouchers.ingresos_cs) }}</strong>
      </article>
      <article class="reports-kpi">
        <span>Egresos caja</span>
        <strong>C$ {{ formatMoney(summary.cash_vouchers.egresos_cs) }}</strong>
      </article>
      <article class="reports-kpi">
        <span>Productos activos</span>
        <strong>{{ summary.inventory.product_count }}</strong>
      </article>
    </section>

    <section class="panel-card reports-table-panel">
      <div class="panel-head">
        <div>
          <span class="products-section-kicker">{{ activeTabMeta.section }}</span>
          <h3>{{ activeTabMeta.label }}</h3>
        </div>
        <Tag severity="info" :value="`${rows.length} registros`" rounded />
      </div>

      <DataTable :value="rows" :loading="loading" class="enterprise-table reports-table" stripedRows paginator :rows="12" responsive-layout="scroll">
        <Column v-for="column in activeColumns" :key="column.field" :field="column.field" :header="column.header" sortable>
          <template #body="{ data }">
            <span v-if="column.type === 'money'">C$ {{ formatMoney(data[column.field]) }}</span>
            <span v-else-if="column.type === 'usd'">US$ {{ formatMoney(data[column.field]) }}</span>
            <Tag v-else-if="column.type === 'tag'" :severity="tagSeverity(data[column.field])" :value="data[column.field]" rounded />
            <span v-else>{{ data[column.field] }}</span>
          </template>
        </Column>
        <template #empty>
          <div class="empty-state">No hay datos para los filtros seleccionados.</div>
        </template>
      </DataTable>
    </section>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import Button from "primevue/button";
import Column from "primevue/column";
import DataTable from "primevue/datatable";
import InputText from "primevue/inputtext";
import Select from "primevue/select";
import Tag from "primevue/tag";
import { useToast } from "primevue/usetoast";

import {
  fetchCashVouchersReport,
  fetchInventoryConsolidatedReport,
  fetchKardexReport,
  fetchLowStockReport,
  fetchNoStockReport,
  fetchProfitReport,
  fetchReportCatalogs,
  fetchReportsSummary,
  fetchSalesDetailedReport,
  fetchSalesProductsReport,
  fetchStagnantProductsReport,
  fetchTopMovementReport,
  fetchWarehouseBalancesReport,
} from "../../services/reports";

const toast = useToast();
const loading = ref(false);
const activeReport = ref("sales-detailed");
const rows = ref([]);
const bodegas = ref([]);
const products = ref([]);

const filters = reactive({
  start_date: firstDayOfMonth(),
  end_date: new Date().toISOString().slice(0, 10),
  bodega_id: null,
  product_id: null,
  days_without_movement: 60,
  max_stock: 5,
});

const summary = reactive({
  sales: { invoice_count: 0, total_cs: 0, total_usd: 0, average_ticket_cs: 0 },
  cash_vouchers: { ingresos_cs: 0, egresos_cs: 0, balance_cs: 0 },
  inventory: { product_count: 0, existencia_total: 0, valor_costo_cs: 0, valor_venta_cs: 0 },
});

const reportTabs = [
  { key: "sales-detailed", label: "Ventas detalladas", section: "Ventas", icon: "bi-receipt-cutoff" },
  { key: "sales-products", label: "Productos vendidos", section: "Ventas", icon: "bi-box-seam" },
  { key: "profit", label: "Utilidad", section: "Ventas", icon: "bi-graph-up" },
  { key: "inventory-consolidated", label: "Inventario consolidado", section: "Inventario", icon: "bi-boxes" },
  { key: "saldos-bodega", label: "Saldos por bodega", section: "Inventario", icon: "bi-building" },
  { key: "kardex", label: "Kardex", section: "Inventario", icon: "bi-list-columns-reverse" },
  { key: "cash-vouchers", label: "Vales de caja", section: "Caja", icon: "bi-cash-stack" },
  { key: "stagnant-products", label: "Productos estancados", section: "Analisis especial", icon: "bi-hourglass-split" },
  { key: "top-movement", label: "Mayor movimiento", section: "Analisis especial", icon: "bi-arrow-repeat" },
  { key: "low-stock", label: "Bajo stock", section: "Analisis especial", icon: "bi-exclamation-triangle" },
  { key: "no-stock", label: "Sin existencia", section: "Analisis especial", icon: "bi-x-circle" },
];

const reportColumns = {
  "sales-detailed": [
    { field: "fecha", header: "Fecha" },
    { field: "invoice_number", header: "Factura" },
    { field: "customer_name", header: "Cliente" },
    { field: "vendor_name", header: "Vendedor" },
    { field: "bodega", header: "Bodega" },
    { field: "total_cs", header: "Total C$", type: "money" },
    { field: "balance_cs", header: "Saldo C$", type: "money" },
    { field: "status", header: "Estado", type: "tag" },
  ],
  "sales-products": [
    { field: "cod_producto", header: "Codigo" },
    { field: "descripcion", header: "Producto" },
    { field: "cantidad", header: "Cantidad" },
    { field: "subtotal_cs", header: "Venta C$", type: "money" },
    { field: "subtotal_usd", header: "Venta US$", type: "usd" },
  ],
  profit: [
    { field: "cod_producto", header: "Codigo" },
    { field: "descripcion", header: "Producto" },
    { field: "cantidad", header: "Cantidad" },
    { field: "venta_cs", header: "Venta C$", type: "money" },
    { field: "costo_cs", header: "Costo C$", type: "money" },
    { field: "utilidad_cs", header: "Utilidad C$", type: "money" },
  ],
  "inventory-consolidated": [
    { field: "cod_producto", header: "Codigo" },
    { field: "descripcion", header: "Producto" },
    { field: "linea", header: "Linea" },
    { field: "segmento", header: "Segmento" },
    { field: "existencia", header: "Existencia" },
    { field: "valor_costo_cs", header: "Costo total", type: "money" },
    { field: "valor_venta_cs", header: "Venta estimada", type: "money" },
  ],
  "saldos-bodega": [
    { field: "bodega", header: "Bodega" },
    { field: "cod_producto", header: "Codigo" },
    { field: "descripcion", header: "Producto" },
    { field: "existencia", header: "Existencia" },
    { field: "valor_costo_cs", header: "Costo total", type: "money" },
  ],
  kardex: [
    { field: "fecha", header: "Fecha" },
    { field: "tipo", header: "Tipo", type: "tag" },
    { field: "documento", header: "Documento" },
    { field: "bodega", header: "Bodega" },
    { field: "cod_producto", header: "Codigo" },
    { field: "descripcion", header: "Producto" },
    { field: "entrada", header: "Entrada" },
    { field: "salida", header: "Salida" },
    { field: "subtotal_cs", header: "Valor C$", type: "money" },
  ],
  "cash-vouchers": [
    { field: "fecha", header: "Fecha" },
    { field: "numero", header: "Numero" },
    { field: "tipo", header: "Tipo", type: "tag" },
    { field: "rubro", header: "Rubro" },
    { field: "motivo", header: "Motivo" },
    { field: "bodega", header: "Bodega" },
    { field: "monto_cs", header: "Monto C$", type: "money" },
    { field: "status", header: "Estado", type: "tag" },
  ],
  "stagnant-products": [
    { field: "cod_producto", header: "Codigo" },
    { field: "descripcion", header: "Producto" },
    { field: "linea", header: "Linea" },
    { field: "segmento", header: "Segmento" },
    { field: "existencia", header: "Existencia" },
    { field: "ultimo_movimiento", header: "Ultimo movimiento" },
    { field: "dias_sin_movimiento", header: "Dias" },
    { field: "valor_costo_cs", header: "Valor estancado", type: "money" },
  ],
  "top-movement": [
    { field: "cod_producto", header: "Codigo" },
    { field: "descripcion", header: "Producto" },
    { field: "entradas", header: "Entradas" },
    { field: "salidas", header: "Salidas" },
    { field: "movimiento_total", header: "Movimiento total" },
    { field: "rotacion_neta", header: "Rotacion neta" },
    { field: "valor_salidas_cs", header: "Valor salidas", type: "money" },
  ],
  "low-stock": [
    { field: "cod_producto", header: "Codigo" },
    { field: "descripcion", header: "Producto" },
    { field: "linea", header: "Linea" },
    { field: "existencia", header: "Existencia" },
    { field: "costo_producto", header: "Costo unitario", type: "money" },
    { field: "valor_costo_cs", header: "Valor C$", type: "money" },
  ],
  "no-stock": [
    { field: "cod_producto", header: "Codigo" },
    { field: "descripcion", header: "Producto" },
    { field: "linea", header: "Linea" },
    { field: "segmento", header: "Segmento" },
    { field: "existencia", header: "Existencia" },
    { field: "precio_venta1", header: "Precio venta", type: "money" },
  ],
};

const activeTabMeta = computed(() => reportTabs.find((tab) => tab.key === activeReport.value) || reportTabs[0]);
const activeColumns = computed(() => reportColumns[activeReport.value] || []);

async function loadActiveReport() {
  loading.value = true;
  try {
    await loadSummary();
    const reportFilters = {
      start_date: filters.start_date,
      end_date: filters.end_date,
      bodega_id: filters.bodega_id,
    };
    const loaders = {
      "sales-detailed": () => fetchSalesDetailedReport(reportFilters),
      "sales-products": () => fetchSalesProductsReport(reportFilters),
      profit: () => fetchProfitReport(reportFilters),
      "inventory-consolidated": () => fetchInventoryConsolidatedReport(),
      "saldos-bodega": () => fetchWarehouseBalancesReport({ bodega_id: filters.bodega_id }),
      kardex: () => fetchKardexReport({ ...reportFilters, product_id: filters.product_id }),
      "cash-vouchers": () => fetchCashVouchersReport(reportFilters),
      "stagnant-products": () => fetchStagnantProductsReport({
        bodega_id: filters.bodega_id,
        days_without_movement: filters.days_without_movement,
      }),
      "top-movement": () => fetchTopMovementReport({ ...reportFilters, limit: 100 }),
      "low-stock": () => fetchLowStockReport({ bodega_id: filters.bodega_id, max_stock: filters.max_stock }),
      "no-stock": () => fetchNoStockReport(),
    };
    rows.value = await loaders[activeReport.value]();
  } catch (error) {
    rows.value = [];
    toast.add({ severity: "error", summary: "No se pudo cargar informe", detail: error.message, life: 4200 });
  } finally {
    loading.value = false;
  }
}

async function loadSummary() {
  const data = await fetchReportsSummary({
    start_date: filters.start_date,
    end_date: filters.end_date,
    bodega_id: filters.bodega_id,
  });
  Object.assign(summary.sales, data.sales || {});
  Object.assign(summary.cash_vouchers, data.cash_vouchers || {});
  Object.assign(summary.inventory, data.inventory || {});
}

async function loadCatalogs() {
  const catalogs = await fetchReportCatalogs();
  bodegas.value = catalogs.bodegas || [];
  products.value = catalogs.products || [];
}

function selectReport(key) {
  activeReport.value = key;
  loadActiveReport();
}

function firstDayOfMonth() {
  const now = new Date();
  return new Date(now.getFullYear(), now.getMonth(), 1).toISOString().slice(0, 10);
}

function formatMoney(value) {
  return new Intl.NumberFormat("es-NI", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(value || 0));
}

function tagSeverity(value) {
  const text = String(value || "").toLowerCase();
  if (text.includes("ingreso") || text.includes("emitida") || text.includes("emitido")) return "success";
  if (text.includes("egreso") || text.includes("cerrado")) return "warn";
  if (text.includes("anulada")) return "danger";
  return "info";
}

function printReport() {
  window.print();
}

function exportCsv() {
  const columns = activeColumns.value;
  const header = columns.map((column) => column.header).join(",");
  const body = rows.value.map((row) =>
    columns.map((column) => `"${String(row[column.field] ?? "").replaceAll('"', '""')}"`).join(","),
  );
  const blob = new Blob([[header, ...body].join("\n")], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `${activeReport.value}_${filters.start_date}_${filters.end_date}.csv`;
  link.click();
  URL.revokeObjectURL(url);
}

onMounted(async () => {
  loading.value = true;
  try {
    await loadCatalogs();
    await loadActiveReport();
  } catch (error) {
    toast.add({ severity: "error", summary: "No se pudo cargar informes", detail: error.message, life: 4200 });
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.reports-filter-panel,
.reports-table-panel {
  margin-bottom: 1rem;
}

.reports-filter-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 0.8rem;
  align-items: end;
}

.reports-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  justify-content: flex-end;
  grid-column: span 2;
}

.reports-tabs {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin: 0 0 1rem;
}

.reports-tabs button {
  border: 1px solid rgba(148, 163, 184, 0.42);
  border-radius: 8px;
  background: #fff;
  color: #334155;
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  min-height: 2.35rem;
  padding: 0.45rem 0.7rem;
  font-weight: 700;
  cursor: pointer;
}

.reports-tabs button.active {
  background: #0f172a;
  border-color: #0f172a;
  color: #fff;
}

.reports-kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.reports-kpi {
  border: 1px solid rgba(148, 163, 184, 0.35);
  border-radius: 8px;
  background: #fff;
  padding: 0.85rem 1rem;
}

.reports-kpi span {
  display: block;
  color: #64748b;
  font-size: 0.78rem;
}

.reports-kpi strong {
  color: #0f172a;
  display: block;
  font-size: 1.15rem;
  margin-top: 0.2rem;
}

@media (max-width: 1100px) {
  .reports-filter-grid,
  .reports-kpi-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .reports-actions {
    justify-content: flex-start;
  }
}

@media (max-width: 720px) {
  .reports-filter-grid,
  .reports-kpi-grid {
    grid-template-columns: 1fr;
  }
}

@media print {
  .reports-hero,
  .reports-filter-panel,
  .reports-tabs,
  .enterprise-topbar,
  .app-sidebar {
    display: none !important;
  }

  .reports-table-panel {
    border: 0;
    box-shadow: none;
  }
}
</style>
