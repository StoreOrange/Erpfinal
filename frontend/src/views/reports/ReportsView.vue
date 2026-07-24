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
        <label v-if="showDateFilters" class="field-group">
          <span>Desde</span>
          <InputText v-model="filters.start_date" type="date" />
        </label>
        <label v-if="showDateFilters" class="field-group">
          <span>Hasta</span>
          <InputText v-model="filters.end_date" type="date" />
        </label>
        <label class="field-group">
          <span>Bodega</span>
          <Select v-model="filters.bodega_id" :options="filteredBodegas" option-label="name" option-value="id" show-clear filter placeholder="Todas" />
        </label>
        <label class="field-group">
          <span>Sucursal</span>
          <Select v-model="filters.sucursal_id" :options="sucursales" option-label="name" option-value="id" show-clear filter placeholder="Todas" />
        </label>
        <label v-if="activeReport === 'kardex'" class="field-group">
          <span>Producto para kardex</span>
          <Select v-model="filters.product_id" :options="products" option-label="descripcion" option-value="id" show-clear filter placeholder="Todos" />
        </label>
        <label v-if="activeReport === 'stagnant-products'" class="field-group">
          <span>Dias sin movimiento</span>
          <InputText v-model.number="filters.days_without_movement" type="number" min="1" />
        </label>
        <label v-if="activeReport === 'low-stock'" class="field-group">
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

      <div v-if="isSalesDashboardReport" class="sales-dashboard-report">
        <div class="sales-dashboard-kpis">
          <article>
            <span>Ventas del periodo</span>
            <strong>C$ {{ formatMoney(salesDashboard.period.total_cs) }}</strong>
            <small>{{ salesDashboard.period.invoice_count }} facturas</small>
          </article>
          <article>
            <span>Acumulado del mes</span>
            <strong>C$ {{ formatMoney(salesDashboard.month.total_cs) }}</strong>
            <small>{{ salesDashboard.month.invoice_count }} facturas</small>
          </article>
          <article>
            <span>Ticket promedio</span>
            <strong>C$ {{ formatMoney(salesDashboard.period.average_ticket_cs) }}</strong>
            <small>Periodo seleccionado</small>
          </article>
          <article>
            <span>Mejor dia del mes</span>
            <strong>{{ salesDashboard.month.top_day?.fecha || "-" }}</strong>
            <small>C$ {{ formatMoney(salesDashboard.month.top_day?.total_cs) }}</small>
          </article>
        </div>

        <div class="sales-dashboard-grid">
          <section class="sales-dashboard-chart">
            <div class="dashboard-chart-head">
              <span>Ventas por dia</span>
              <strong>Acumulado mensual</strong>
            </div>
            <VueApexCharts type="bar" height="260" :options="dailySalesChartOptions" :series="dailySalesChartSeries" />
          </section>
          <section class="sales-dashboard-chart">
            <div class="dashboard-chart-head">
              <span>Ventas por bodega</span>
              <strong>Periodo seleccionado</strong>
            </div>
            <VueApexCharts type="bar" height="260" :options="warehouseSalesChartOptions" :series="warehouseSalesChartSeries" />
          </section>
        </div>

        <div class="sales-dashboard-grid">
          <section>
            <h4>Ventas por sucursal</h4>
            <DataTable :value="salesDashboard.by_branch" class="enterprise-table reports-table compact-table" responsive-layout="scroll">
              <Column field="sucursal" header="Sucursal" />
              <Column field="invoice_count" header="Facturas" />
              <Column field="total_cs" header="Venta C$">
                <template #body="{ data }">C$ {{ formatMoney(data.total_cs) }}</template>
              </Column>
              <Column field="total_usd" header="Venta US$">
                <template #body="{ data }">US$ {{ formatMoney(data.total_usd) }}</template>
              </Column>
            </DataTable>
          </section>
          <section>
            <h4>Comparativo trimestral</h4>
            <DataTable :value="salesDashboard.quarterly" class="enterprise-table reports-table compact-table" responsive-layout="scroll">
              <Column field="quarter" header="Trimestre" />
              <Column field="invoice_count" header="Facturas" />
              <Column field="total_cs" header="Venta C$">
                <template #body="{ data }">C$ {{ formatMoney(data.total_cs) }}</template>
              </Column>
              <Column field="variation_percent" header="Var. %">
                <template #body="{ data }">{{ formatPercent(data.variation_percent) }}</template>
              </Column>
            </DataTable>
          </section>
        </div>
      </div>

      <div v-else-if="isInventoryExistencesReport" class="inventory-existence-report">
        <div class="inventory-existence-summary">
          <div>
            <span>Bodegas visibles</span>
            <strong>{{ inventoryMatrix.bodegas.length }}</strong>
          </div>
          <div>
            <span>Productos con existencia</span>
            <strong>{{ inventoryMatrix.rows.length }}</strong>
          </div>
          <div>
            <span>Unidades totales</span>
            <strong>{{ formatQty(inventoryMatrix.totals.grand_total) }}</strong>
          </div>
          <div>
            <span>Costo estimado</span>
            <strong>C$ {{ formatMoney(inventoryMatrix.totals.valor_costo_cs) }}</strong>
          </div>
        </div>

        <div class="inventory-existence-scroll">
          <table class="inventory-existence-table">
            <thead>
              <tr>
                <th class="inventory-product-code">Codigo</th>
                <th class="inventory-product-name">Articulo</th>
                <th v-for="bodega in inventoryMatrix.bodegas" :key="bodega.id" class="inventory-qty-col">
                  <span>{{ bodega.name }}</span>
                  <small>{{ bodega.sucursal || bodega.code }}</small>
                </th>
                <th class="inventory-total-col">Total</th>
                <th class="inventory-money-col">Costo C$</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in inventoryMatrix.rows" :key="item.id">
                <td class="inventory-product-code">{{ item.cod_producto }}</td>
                <td class="inventory-product-name">
                  <strong>{{ item.descripcion }}</strong>
                  <small>{{ [item.linea, item.segmento].filter(Boolean).join(" / ") }}</small>
                </td>
                <td v-for="bodega in inventoryMatrix.bodegas" :key="`${item.id}-${bodega.id}`" class="inventory-qty-col">
                  <span :class="{ muted: stockByBodega(item, bodega.id) === 0 }">
                    {{ formatQty(stockByBodega(item, bodega.id)) }}
                  </span>
                </td>
                <td class="inventory-total-col">{{ formatQty(item.total_existencia) }}</td>
                <td class="inventory-money-col">C$ {{ formatMoney(item.valor_costo_cs) }}</td>
              </tr>
            </tbody>
            <tfoot>
              <tr>
                <td colspan="2">Totales por bodega</td>
                <td v-for="bodega in inventoryMatrix.bodegas" :key="`total-${bodega.id}`" class="inventory-qty-col">
                  {{ formatQty(inventoryMatrix.totals.by_bodega[String(bodega.id)] || 0) }}
                </td>
                <td class="inventory-total-col">{{ formatQty(inventoryMatrix.totals.grand_total) }}</td>
                <td class="inventory-money-col">C$ {{ formatMoney(inventoryMatrix.totals.valor_costo_cs) }}</td>
              </tr>
            </tfoot>
          </table>
          <div v-if="!inventoryMatrix.rows.length && !loading" class="empty-state">No hay existencias para los filtros seleccionados.</div>
        </div>
      </div>

      <DataTable v-else :value="rows" :loading="loading" class="enterprise-table reports-table" stripedRows paginator :rows="12" responsive-layout="scroll">
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
import { computed, onMounted, reactive, ref, watch } from "vue";
import Button from "primevue/button";
import Column from "primevue/column";
import DataTable from "primevue/datatable";
import InputText from "primevue/inputtext";
import Select from "primevue/select";
import Tag from "primevue/tag";
import { useToast } from "primevue/usetoast";
import VueApexCharts from "vue3-apexcharts";

import {
  fetchCashVouchersReport,
  fetchInventoryConsolidatedReport,
  fetchInventoryExistencesReport,
  fetchKardexReport,
  fetchLowStockReport,
  fetchNoStockReport,
  fetchProfitReport,
  fetchReportCatalogs,
  fetchReportsSummary,
  fetchSalesDashboardReport,
  fetchSalesDetailedReport,
  fetchSalesProductsReport,
  fetchStagnantProductsReport,
  fetchTopMovementReport,
  fetchWarehouseBalancesReport,
} from "../../services/reports";

const toast = useToast();
const loading = ref(false);
const activeReport = ref("sales-dashboard");
const rows = ref([]);
const bodegas = ref([]);
const sucursales = ref([]);
const products = ref([]);
const inventoryMatrix = reactive({
  bodegas: [],
  rows: [],
  totals: { by_bodega: {}, grand_total: 0, valor_costo_cs: 0 },
});
const salesDashboard = reactive({
  period: { invoice_count: 0, total_cs: 0, total_usd: 0, average_ticket_cs: 0 },
  month: { invoice_count: 0, total_cs: 0, total_usd: 0, average_ticket_cs: 0, top_day: null },
  daily_sales: [],
  by_branch: [],
  by_warehouse: [],
  quarterly: [],
});

const filters = reactive({
  start_date: firstDayOfMonth(),
  end_date: new Date().toISOString().slice(0, 10),
  sucursal_id: null,
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
  { key: "sales-dashboard", label: "Dashboard ventas", section: "Ventas", icon: "bi-speedometer2" },
  { key: "sales-detailed", label: "Ventas detalladas", section: "Ventas", icon: "bi-receipt-cutoff" },
  { key: "sales-products", label: "Productos vendidos", section: "Ventas", icon: "bi-box-seam" },
  { key: "profit", label: "Utilidad", section: "Ventas", icon: "bi-graph-up" },
  { key: "inventory-consolidated", label: "Inventario consolidado", section: "Inventario", icon: "bi-boxes" },
  { key: "inventory-existences", label: "Inventario de existencias", section: "Inventario", icon: "bi-grid-3x3-gap" },
  { key: "saldos-bodega", label: "Saldos por bodega", section: "Inventario", icon: "bi-building" },
  { key: "kardex", label: "Kardex", section: "Inventario", icon: "bi-list-columns-reverse" },
  { key: "cash-vouchers", label: "Vales de caja", section: "Caja", icon: "bi-cash-stack" },
  { key: "stagnant-products", label: "Productos estancados", section: "Analisis especial", icon: "bi-hourglass-split" },
  { key: "top-movement", label: "Mayor movimiento", section: "Analisis especial", icon: "bi-arrow-repeat" },
  { key: "low-stock", label: "Bajo stock", section: "Analisis especial", icon: "bi-exclamation-triangle" },
  { key: "no-stock", label: "Sin existencia", section: "Analisis especial", icon: "bi-x-circle" },
];

const reportColumns = {
  "sales-dashboard": [
    { field: "fecha", header: "Fecha" },
    { field: "invoice_count", header: "Facturas" },
    { field: "total_cs", header: "Venta C$", type: "money" },
    { field: "accumulated_cs", header: "Acumulado C$", type: "money" },
  ],
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
const isSalesDashboardReport = computed(() => activeReport.value === "sales-dashboard");
const isInventoryExistencesReport = computed(() => activeReport.value === "inventory-existences");
const showDateFilters = computed(() =>
  ["sales-dashboard", "sales-detailed", "sales-products", "profit", "kardex", "cash-vouchers", "top-movement"].includes(activeReport.value),
);
const filteredBodegas = computed(() => {
  if (!filters.sucursal_id) return bodegas.value;
  return bodegas.value.filter((bodega) => Number(bodega.sucursal_id) === Number(filters.sucursal_id));
});

const dailySalesChartOptions = computed(() => ({
  chart: { toolbar: { show: false }, fontFamily: "Inter, system-ui, sans-serif" },
  colors: ["#0f172a", "#16a34a"],
  dataLabels: { enabled: false },
  grid: { borderColor: "#e2e8f0" },
  plotOptions: { bar: { borderRadius: 4, columnWidth: "52%" } },
  stroke: { width: [0, 3], curve: "smooth" },
  xaxis: {
    categories: salesDashboard.daily_sales.map((row) => row.fecha.slice(8, 10)),
    labels: { style: { colors: "#64748b", fontSize: "11px" } },
  },
  yaxis: { labels: { formatter: (value) => `C$ ${formatCompactMoney(value)}` } },
  tooltip: { y: { formatter: (value) => `C$ ${formatMoney(value)}` } },
}));

const dailySalesChartSeries = computed(() => [
  { name: "Venta diaria", type: "column", data: salesDashboard.daily_sales.map((row) => Number(row.total_cs || 0)) },
  { name: "Acumulado", type: "line", data: salesDashboard.daily_sales.map((row) => Number(row.accumulated_cs || 0)) },
]);

const warehouseSalesChartOptions = computed(() => ({
  chart: { toolbar: { show: false }, fontFamily: "Inter, system-ui, sans-serif" },
  colors: ["#2563eb"],
  dataLabels: { enabled: false },
  grid: { borderColor: "#e2e8f0" },
  plotOptions: { bar: { borderRadius: 4, horizontal: true, barHeight: "56%" } },
  xaxis: { labels: { formatter: (value) => `C$ ${formatCompactMoney(value)}` } },
  yaxis: {
    labels: {
      maxWidth: 130,
      style: { colors: "#334155", fontSize: "11px" },
    },
  },
  tooltip: { y: { formatter: (value) => `C$ ${formatMoney(value)}` } },
}));

const warehouseSalesChartSeries = computed(() => [
  {
    name: "Ventas",
    data: salesDashboard.by_warehouse.slice(0, 10).map((row) => ({
      x: row.bodega,
      y: Number(row.total_cs || 0),
    })),
  },
]);

async function loadActiveReport() {
  loading.value = true;
  try {
    await loadSummary();
    const reportFilters = {
      start_date: filters.start_date,
      end_date: filters.end_date,
      sucursal_id: filters.sucursal_id,
      bodega_id: filters.bodega_id,
    };
    const loaders = {
      "sales-dashboard": () => fetchSalesDashboardReport(reportFilters),
      "sales-detailed": () => fetchSalesDetailedReport(reportFilters),
      "sales-products": () => fetchSalesProductsReport(reportFilters),
      profit: () => fetchProfitReport(reportFilters),
      "inventory-consolidated": () => fetchInventoryConsolidatedReport(),
      "inventory-existences": () => fetchInventoryExistencesReport({
        sucursal_id: filters.sucursal_id,
        bodega_id: filters.bodega_id,
      }),
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
    const data = await loaders[activeReport.value]();
    if (isSalesDashboardReport.value) {
      applySalesDashboard(data);
      rows.value = salesDashboard.daily_sales;
      applyInventoryMatrix();
    } else if (isInventoryExistencesReport.value) {
      applyInventoryMatrix(data);
      rows.value = inventoryMatrix.rows;
      applySalesDashboard();
    } else {
      rows.value = data;
      applyInventoryMatrix();
      applySalesDashboard();
    }
  } catch (error) {
    rows.value = [];
    applyInventoryMatrix();
    applySalesDashboard();
    toast.add({ severity: "error", summary: "No se pudo cargar informe", detail: error.message, life: 4200 });
  } finally {
    loading.value = false;
  }
}

async function loadSummary() {
  const data = await fetchReportsSummary({
    start_date: filters.start_date,
    end_date: filters.end_date,
    sucursal_id: filters.sucursal_id,
    bodega_id: filters.bodega_id,
  });
  Object.assign(summary.sales, data.sales || {});
  Object.assign(summary.cash_vouchers, data.cash_vouchers || {});
  Object.assign(summary.inventory, data.inventory || {});
}

async function loadCatalogs() {
  const catalogs = await fetchReportCatalogs();
  sucursales.value = catalogs.sucursales || [];
  bodegas.value = catalogs.bodegas || [];
  products.value = catalogs.products || [];
}

function applyInventoryMatrix(data = null) {
  inventoryMatrix.bodegas = data?.bodegas || [];
  inventoryMatrix.rows = data?.rows || [];
  inventoryMatrix.totals = data?.totals || { by_bodega: {}, grand_total: 0, valor_costo_cs: 0 };
}

function applySalesDashboard(data = null) {
  salesDashboard.period = data?.period || { invoice_count: 0, total_cs: 0, total_usd: 0, average_ticket_cs: 0 };
  salesDashboard.month = data?.month || { invoice_count: 0, total_cs: 0, total_usd: 0, average_ticket_cs: 0, top_day: null };
  salesDashboard.daily_sales = data?.daily_sales || [];
  salesDashboard.by_branch = data?.by_branch || [];
  salesDashboard.by_warehouse = data?.by_warehouse || [];
  salesDashboard.quarterly = data?.quarterly || [];
}

function selectReport(key) {
  activeReport.value = key;
  loadActiveReport();
}

watch(
  () => filters.sucursal_id,
  () => {
    if (filters.bodega_id && !filteredBodegas.value.some((bodega) => Number(bodega.id) === Number(filters.bodega_id))) {
      filters.bodega_id = null;
    }
  },
);

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

function formatQty(value) {
  return new Intl.NumberFormat("es-NI", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(value || 0));
}

function formatPercent(value) {
  return `${new Intl.NumberFormat("es-NI", {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  }).format(Number(value || 0))}%`;
}

function formatCompactMoney(value) {
  return new Intl.NumberFormat("es-NI", {
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(Number(value || 0));
}

function stockByBodega(item, bodegaId) {
  return Number(item?.balances?.[String(bodegaId)] || 0);
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
  if (isSalesDashboardReport.value) {
    exportSalesDashboardCsv();
    return;
  }
  if (isInventoryExistencesReport.value) {
    exportInventoryMatrixCsv();
    return;
  }
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

function exportSalesDashboardCsv() {
  const sections = [];
  sections.push("VENTAS POR DIA");
  sections.push(["Fecha", "Facturas", "Venta C$", "Acumulado C$"].join(","));
  salesDashboard.daily_sales.forEach((row) => {
    sections.push([row.fecha, row.invoice_count, row.total_cs, row.accumulated_cs].map((value) => `"${String(value ?? "").replaceAll('"', '""')}"`).join(","));
  });
  sections.push("");
  sections.push("VENTAS POR SUCURSAL");
  sections.push(["Sucursal", "Facturas", "Venta C$", "Venta US$"].join(","));
  salesDashboard.by_branch.forEach((row) => {
    sections.push([row.sucursal, row.invoice_count, row.total_cs, row.total_usd].map((value) => `"${String(value ?? "").replaceAll('"', '""')}"`).join(","));
  });
  sections.push("");
  sections.push("COMPARATIVO TRIMESTRAL");
  sections.push(["Trimestre", "Facturas", "Venta C$", "Variacion %"].join(","));
  salesDashboard.quarterly.forEach((row) => {
    sections.push([row.quarter, row.invoice_count, row.total_cs, row.variation_percent].map((value) => `"${String(value ?? "").replaceAll('"', '""')}"`).join(","));
  });
  const blob = new Blob([sections.join("\n")], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `dashboard_ventas_${filters.start_date}_${filters.end_date}.csv`;
  link.click();
  URL.revokeObjectURL(url);
}

function exportInventoryMatrixCsv() {
  const header = [
    "Codigo",
    "Articulo",
    ...inventoryMatrix.bodegas.map((bodega) => bodega.name),
    "Total",
    "Costo C$",
  ].join(",");
  const body = inventoryMatrix.rows.map((row) =>
    [
      row.cod_producto,
      row.descripcion,
      ...inventoryMatrix.bodegas.map((bodega) => stockByBodega(row, bodega.id)),
      row.total_existencia,
      row.valor_costo_cs,
    ].map((value) => `"${String(value ?? "").replaceAll('"', '""')}"`).join(","),
  );
  const footer = [
    "TOTALES",
    "",
    ...inventoryMatrix.bodegas.map((bodega) => inventoryMatrix.totals.by_bodega[String(bodega.id)] || 0),
    inventoryMatrix.totals.grand_total,
    inventoryMatrix.totals.valor_costo_cs,
  ].map((value) => `"${String(value ?? "").replaceAll('"', '""')}"`).join(",");
  const blob = new Blob([[header, ...body, footer].join("\n")], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `inventario_existencias_${filters.start_date}_${filters.end_date}.csv`;
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
  margin-bottom: 0.7rem;
}

.reports-filter-panel {
  padding: 0.8rem 0.9rem;
}

.reports-table-panel {
  padding: 0.75rem 0.85rem;
}

.reports-table-panel .panel-head {
  margin-bottom: 0.55rem;
}

.reports-table-panel .panel-head h3 {
  font-size: 1rem;
  margin: 0;
}

.reports-filter-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(10.5rem, 1fr));
  gap: 0.55rem;
  align-items: end;
}

.reports-filter-grid .field-group {
  gap: 0.18rem;
  min-height: auto;
}

.reports-filter-grid .field-group > span {
  font-size: 0.66rem;
  line-height: 1.1;
}

.reports-filter-grid :deep(.p-inputtext),
.reports-filter-grid :deep(.p-select) {
  min-height: 2rem;
  height: 2rem;
  font-size: 0.78rem;
}

.reports-filter-grid :deep(.p-select-label) {
  padding-top: 0.34rem;
  padding-bottom: 0.34rem;
  font-size: 0.78rem;
}

.reports-actions {
  display: flex;
  gap: 0.38rem;
  flex-wrap: wrap;
  justify-content: flex-end;
  align-items: end;
}

.reports-actions :deep(.p-button) {
  min-height: 2rem;
  padding: 0.35rem 0.6rem;
  font-size: 0.78rem;
}

.reports-tabs {
  display: flex;
  gap: 0.35rem;
  flex-wrap: wrap;
  margin: 0 0 0.65rem;
}

.reports-tabs button {
  border: 1px solid rgba(148, 163, 184, 0.42);
  border-radius: 7px;
  background: #fff;
  color: #334155;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  min-height: 1.95rem;
  padding: 0.3rem 0.52rem;
  font-size: 0.76rem;
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
  gap: 0.55rem;
  margin-bottom: 0.7rem;
}

.reports-kpi {
  border: 1px solid rgba(148, 163, 184, 0.35);
  border-radius: 8px;
  background: #fff;
  padding: 0.58rem 0.7rem;
}

.reports-kpi span {
  display: block;
  color: #64748b;
  font-size: 0.68rem;
}

.reports-kpi strong {
  color: #0f172a;
  display: block;
  font-size: 0.96rem;
  margin-top: 0.12rem;
}

.sales-dashboard-report {
  display: grid;
  gap: 0.7rem;
}

.sales-dashboard-kpis {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.55rem;
}

.sales-dashboard-kpis article,
.sales-dashboard-chart,
.sales-dashboard-grid > section {
  border: 1px solid rgba(148, 163, 184, 0.35);
  border-radius: 8px;
  background: #fff;
}

.sales-dashboard-kpis article {
  padding: 0.65rem 0.75rem;
}

.sales-dashboard-kpis span,
.dashboard-chart-head span {
  display: block;
  color: #64748b;
  font-size: 0.68rem;
  font-weight: 700;
}

.sales-dashboard-kpis strong {
  color: #0f172a;
  display: block;
  font-size: 1.05rem;
  margin-top: 0.12rem;
}

.sales-dashboard-kpis small {
  color: #64748b;
  display: block;
  font-size: 0.68rem;
  margin-top: 0.08rem;
}

.sales-dashboard-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.65rem;
}

.sales-dashboard-chart,
.sales-dashboard-grid > section {
  min-width: 0;
  padding: 0.65rem;
}

.dashboard-chart-head {
  align-items: baseline;
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.3rem;
}

.dashboard-chart-head strong,
.sales-dashboard-grid h4 {
  color: #0f172a;
  font-size: 0.86rem;
  margin: 0;
}

.compact-table {
  font-size: 0.76rem;
}

.inventory-existence-report {
  display: grid;
  gap: 0.55rem;
}

.inventory-existence-summary {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.45rem;
}

.inventory-existence-summary > div {
  border: 1px solid rgba(148, 163, 184, 0.34);
  border-radius: 8px;
  background: linear-gradient(135deg, #ffffff, #f8fafc);
  padding: 0.5rem 0.65rem;
}

.inventory-existence-summary span {
  display: block;
  color: #64748b;
  font-size: 0.66rem;
  font-weight: 700;
}

.inventory-existence-summary strong {
  display: block;
  color: #0f172a;
  font-size: 0.92rem;
  margin-top: 0.1rem;
}

.inventory-existence-scroll {
  border: 1px solid rgba(148, 163, 184, 0.38);
  border-radius: 8px;
  overflow: auto;
  max-height: 70vh;
  background: #fff;
}

.inventory-existence-table {
  border-collapse: separate;
  border-spacing: 0;
  min-width: max-content;
  width: 100%;
  font-size: 0.74rem;
}

.inventory-existence-table th,
.inventory-existence-table td {
  border-bottom: 1px solid #e2e8f0;
  padding: 0.36rem 0.48rem;
  vertical-align: middle;
  white-space: nowrap;
}

.inventory-existence-table thead th {
  background: #f8fafc;
  color: #334155;
  font-size: 0.66rem;
  letter-spacing: 0;
  position: sticky;
  top: 0;
  z-index: 2;
}

.inventory-existence-table tfoot td {
  background: #0f172a;
  color: #fff;
  font-weight: 800;
  position: sticky;
  bottom: 0;
  z-index: 2;
}

.inventory-product-code {
  font-weight: 800;
  min-width: 5.8rem;
  position: sticky;
  left: 0;
  z-index: 3;
}

th.inventory-product-code {
  background: #f8fafc;
}

td.inventory-product-code {
  background: #fff;
  color: #0f172a;
}

.inventory-product-name {
  min-width: 14rem;
  max-width: 20rem;
  position: sticky;
  left: 5.8rem;
  z-index: 3;
}

th.inventory-product-name {
  background: #f8fafc;
}

td.inventory-product-name {
  background: #fff;
}

.inventory-product-name strong,
.inventory-product-name small,
.inventory-qty-col span,
.inventory-qty-col small {
  display: block;
}

.inventory-product-name strong {
  color: #0f172a;
  white-space: normal;
}

.inventory-product-name small,
.inventory-qty-col small {
  color: #64748b;
  font-size: 0.64rem;
}

.inventory-qty-col,
.inventory-total-col,
.inventory-money-col {
  min-width: 5.8rem;
  text-align: right;
}

.inventory-total-col {
  background: #f1f5f9;
  color: #0f172a;
  font-weight: 800;
}

.inventory-money-col {
  min-width: 7.4rem;
  font-weight: 800;
}

.inventory-qty-col .muted {
  color: #cbd5e1;
}

@media (max-width: 1100px) {
  .reports-filter-grid,
  .reports-kpi-grid,
  .sales-dashboard-kpis,
  .sales-dashboard-grid,
  .inventory-existence-summary {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .reports-actions {
    justify-content: flex-start;
  }
}

@media (max-width: 720px) {
  .reports-filter-grid,
  .reports-kpi-grid,
  .sales-dashboard-kpis,
  .sales-dashboard-grid,
  .inventory-existence-summary {
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
