<template>
  <section class="page-section sales-utilities-page">
    <header class="sales-utilities-header panel-card">
      <div>
        <p class="page-kicker">Ventas y Facturacion</p>
        <h1 class="page-title">Utilidades de facturacion</h1>
        <p class="utilities-caption">Consulta, reimprime y anula facturas emitidas segun permisos del usuario.</p>
      </div>
      <div class="utilities-stats">
        <article>
          <span>Facturas</span>
          <strong>{{ invoices.length }}</strong>
        </article>
        <article>
          <span>Activas</span>
          <strong>{{ activeInvoices }}</strong>
        </article>
        <article>
          <span>Anuladas</span>
          <strong>{{ voidInvoices }}</strong>
        </article>
      </div>
    </header>

    <section class="panel-card utilities-filter-panel">
      <div class="utilities-filter-grid">
        <label class="field-group utilities-search">
          <span>Buscar factura</span>
          <input v-model.trim="filters.q" class="form-control" placeholder="Numero, cliente, vendedor o producto" @keyup.enter="loadInvoices" />
        </label>
        <label class="field-group">
          <span>Desde</span>
          <input v-model="filters.start_date" type="date" class="form-control" />
        </label>
        <label class="field-group">
          <span>Hasta</span>
          <input v-model="filters.end_date" type="date" class="form-control" />
        </label>
        <label class="field-group">
          <span>Estado</span>
          <select v-model="filters.status_filter" class="form-control">
            <option value="TODAS">Todas</option>
            <option value="EMITIDA">Emitidas</option>
            <option value="CREDITO">Credito</option>
            <option value="ANULADA">Anuladas</option>
          </select>
        </label>
        <div class="utilities-filter-actions">
          <Button icon="bi bi-search" label="Filtrar" :loading="loading" @click="loadInvoices" />
          <Button icon="bi bi-eraser" label="Hoy" severity="secondary" variant="outlined" @click="resetToday" />
        </div>
      </div>
    </section>

    <section class="panel-card utilities-table-panel">
      <DataTable :value="invoices" :loading="loading" class="enterprise-table" stripedRows paginator :rows="12" responsive-layout="scroll">
        <Column field="fecha" header="Fecha" sortable />
        <Column field="invoice_number" header="Factura" sortable>
          <template #body="{ data }">
            <button type="button" class="invoice-link" @click="openDetail(data)">{{ data.invoice_number }}</button>
          </template>
        </Column>
        <Column field="customer_name" header="Cliente" sortable />
        <Column field="vendor_name" header="Vendedor" />
        <Column header="Monto">
          <template #body="{ data }">
            <strong>{{ invoiceSymbol(data) }} {{ formatMoney(invoiceTotal(data)) }}</strong>
          </template>
        </Column>
        <Column field="status" header="Estado">
          <template #body="{ data }">
            <Tag :severity="statusSeverity(data.status)" :value="data.status" rounded />
          </template>
        </Column>
        <Column header="Acciones" style="width: 18rem">
          <template #body="{ data }">
            <div class="utilities-row-actions">
              <Button size="small" icon="bi bi-eye" severity="secondary" variant="outlined" aria-label="Detalle" @click="openDetail(data)" />
              <Button
                size="small"
                icon="bi bi-receipt"
                label="POS"
                severity="secondary"
                variant="outlined"
                :disabled="!canReprint"
                @click="openPrint(data, 'pos')"
              />
              <Button
                size="small"
                icon="bi bi-file-earmark-text"
                label="Carta"
                severity="secondary"
                variant="outlined"
                :disabled="!canReprint"
                @click="openPrint(data, 'letter')"
              />
              <Button
                size="small"
                icon="bi bi-x-circle"
                severity="danger"
                variant="outlined"
                aria-label="Anular"
                :disabled="!canVoid || isVoided(data)"
                @click="openVoidDialog(data)"
              />
            </div>
          </template>
        </Column>
      </DataTable>
    </section>

    <Dialog v-model:visible="detailDialog" modal header="Detalle de factura" :style="{ width: 'min(980px, 96vw)' }">
      <div v-if="printPayload" class="utilities-detail-grid">
        <section class="utilities-summary">
          <div><span>Factura</span><strong>{{ printPayload.invoice.invoice_number }}</strong></div>
          <div><span>Cliente</span><strong>{{ printPayload.invoice.customer_name }}</strong></div>
          <div><span>Vendedor</span><strong>{{ printPayload.invoice.vendor_name || '-' }}</strong></div>
          <div><span>Bodega</span><strong>{{ printPayload.invoice.bodega_name || '-' }}</strong></div>
          <div><span>Fecha</span><strong>{{ printPayload.invoice.fecha }}</strong></div>
          <div><span>Total</span><strong>{{ activeSymbol }} {{ formatMoney(activeTotal) }}</strong></div>
        </section>
        <DataTable :value="printPayload.items" class="enterprise-table utilities-items-table" responsive-layout="scroll">
          <Column field="cod_producto" header="Codigo" />
          <Column field="descripcion" header="Descripcion" />
          <Column field="cantidad" header="Cant." />
          <Column header="Precio">
            <template #body="{ data }">{{ activeSymbol }} {{ formatMoney(linePrice(data)) }}</template>
          </Column>
          <Column header="Subtotal">
            <template #body="{ data }">{{ activeSymbol }} {{ formatMoney(lineTotal(data)) }}</template>
          </Column>
        </DataTable>
      </div>
      <template #footer>
        <Button label="Cerrar" severity="secondary" variant="outlined" @click="detailDialog = false" />
      </template>
    </Dialog>

    <Dialog v-model:visible="printDialog" modal :header="printFormat === 'pos' ? 'Reimpresion POS' : 'Reimpresion carta'" :style="{ width: printFormat === 'pos' ? 'min(420px, 94vw)' : 'min(900px, 96vw)' }">
      <div v-if="printPayload" class="print-preview-shell">
        <div class="print-toolbar">
          <Tag :severity="printPayload.invoice.status === 'ANULADA' ? 'danger' : 'success'" :value="printPayload.invoice.status" rounded />
          <Button icon="bi bi-printer" label="Imprimir" @click="printInvoice" />
        </div>
        <div class="invoice-print-area" :class="printFormat === 'pos' ? 'invoice-print-pos' : 'invoice-print-letter'">
          <div class="invoice-print-head">
            <img v-if="printPayload.business.logo_invoice" :src="printPayload.business.logo_invoice" alt="Logo" />
            <h2>{{ printPayload.business.trade_name || printPayload.business.business_name }}</h2>
            <p v-if="printPayload.business.legal_name">{{ printPayload.business.legal_name }}</p>
            <p v-if="printPayload.business.ruc">RUC: {{ printPayload.business.ruc }}</p>
            <p v-if="printPayload.business.address">{{ printPayload.business.address }}</p>
            <p v-if="printPayload.business.phone">Tel: {{ printPayload.business.phone }}</p>
          </div>
          <div class="invoice-print-meta">
            <div><span>Factura</span><strong>{{ printPayload.invoice.invoice_number }}</strong></div>
            <div><span>Fecha</span><strong>{{ formatDateTime(printPayload.invoice) }}</strong></div>
            <div><span>Cliente</span><strong>{{ printPayload.invoice.customer_name }}</strong></div>
            <div><span>Vendedor</span><strong>{{ printPayload.invoice.vendor_name || '-' }}</strong></div>
          </div>
          <table class="invoice-print-table">
            <thead>
              <tr>
                <th>Producto</th>
                <th class="num">Cant.</th>
                <th class="num">Precio</th>
                <th class="num">Total</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in printPayload.items" :key="item.id">
                <td>
                  <strong>{{ item.cod_producto }}</strong>
                  <span>{{ item.descripcion }}</span>
                </td>
                <td class="num">{{ formatQty(item.cantidad) }}</td>
                <td class="num">{{ activeSymbol }} {{ formatMoney(linePrice(item)) }}</td>
                <td class="num">{{ activeSymbol }} {{ formatMoney(lineTotal(item)) }}</td>
              </tr>
            </tbody>
          </table>
          <div class="invoice-print-totals">
            <div><span>Subtotal</span><strong>{{ activeSymbol }} {{ formatMoney(activeSubtotal) }}</strong></div>
            <div><span>Pagado</span><strong>{{ activeSymbol }} {{ formatMoney(activePaid) }}</strong></div>
            <div><span>Total</span><strong>{{ activeSymbol }} {{ formatMoney(activeTotal) }}</strong></div>
          </div>
          <p v-if="printPayload.invoice.status === 'ANULADA'" class="invoice-void-watermark">FACTURA ANULADA</p>
        </div>
      </div>
    </Dialog>

    <Dialog v-model:visible="voidDialog" modal header="Anular factura" :style="{ width: 'min(620px, 94vw)' }">
      <div v-if="selectedInvoice" class="void-box">
        <div>
          <span>Factura</span>
          <strong>{{ selectedInvoice.invoice_number }}</strong>
        </div>
        <div>
          <span>Cliente</span>
          <strong>{{ selectedInvoice.customer_name }}</strong>
        </div>
      </div>
      <label class="field-group mt-3">
        <span>Motivo de anulacion</span>
        <textarea v-model.trim="voidReason" class="form-control" rows="4" placeholder="Describe claramente por que se anula la factura"></textarea>
      </label>
      <template #footer>
        <Button label="Cancelar" severity="secondary" variant="outlined" @click="voidDialog = false" />
        <Button icon="bi bi-x-circle" label="Anular factura" severity="danger" :loading="voiding" :disabled="!canVoid" @click="confirmVoid" />
      </template>
    </Dialog>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import Button from "primevue/button";
import Column from "primevue/column";
import DataTable from "primevue/datatable";
import Dialog from "primevue/dialog";
import Tag from "primevue/tag";
import { useToast } from "primevue/usetoast";
import { fetchCurrentUser, readStoredUser } from "../../services/auth";
import { fetchSalesInvoicePrint, fetchSalesInvoices, voidSalesInvoice } from "../../services/sales";

const toast = useToast();
const today = new Date().toISOString().slice(0, 10);
const filters = reactive({
  q: "",
  start_date: today,
  end_date: today,
  status_filter: "TODAS",
});
const invoices = ref([]);
const loading = ref(false);
const voiding = ref(false);
const detailDialog = ref(false);
const printDialog = ref(false);
const voidDialog = ref(false);
const printPayload = ref(null);
const printFormat = ref("pos");
const selectedInvoice = ref(null);
const voidReason = ref("");
const currentUser = ref(readStoredUser() || {});

const permissionNames = computed(() => new Set((currentUser.value.permissions || []).map((permission) => permission.name)));
const canReprint = computed(() => permissionNames.value.has("access.sales.invoice_reprint") || permissionNames.value.has("access.sales.utilities"));
const canVoid = computed(() => permissionNames.value.has("access.sales.invoice_void"));
const activeInvoices = computed(() => invoices.value.filter((invoice) => !isVoided(invoice)).length);
const voidInvoices = computed(() => invoices.value.filter((invoice) => isVoided(invoice)).length);
const activeCurrency = computed(() => (printPayload.value?.invoice?.moneda || "CS").toUpperCase());
const activeSymbol = computed(() => (activeCurrency.value === "USD" ? "US$" : "C$"));
const activeSubtotal = computed(() => moneyByCurrency(printPayload.value?.invoice, "subtotal"));
const activeTotal = computed(() => moneyByCurrency(printPayload.value?.invoice, "total"));
const activePaid = computed(() => moneyByCurrency(printPayload.value?.invoice, "paid"));

function moneyByCurrency(invoice, field) {
  if (!invoice) return 0;
  return Number(invoice[`${field}_${activeCurrency.value.toLowerCase()}`] || 0);
}

function invoiceSymbol(invoice) {
  return (invoice.moneda || "CS").toUpperCase() === "USD" ? "US$" : "C$";
}

function invoiceTotal(invoice) {
  return (invoice.moneda || "CS").toUpperCase() === "USD" ? invoice.total_usd : invoice.total_cs;
}

function linePrice(item) {
  return activeCurrency.value === "USD" ? item.precio_unitario_usd : item.precio_unitario_cs;
}

function lineTotal(item) {
  return activeCurrency.value === "USD" ? item.subtotal_usd : item.subtotal_cs;
}

function formatMoney(value) {
  return Number(value || 0).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatQty(value) {
  return Number(value || 0).toLocaleString("en-US", { minimumFractionDigits: 0, maximumFractionDigits: 4 });
}

function isVoided(invoice) {
  return String(invoice?.status || "").toUpperCase() === "ANULADA";
}

function statusSeverity(status) {
  const normalized = String(status || "").toUpperCase();
  if (normalized === "ANULADA") return "danger";
  if (normalized === "CREDITO") return "warn";
  return "success";
}

function formatDateTime(invoice) {
  const datePart = invoice.fecha || "";
  const createdAt = invoice.created_at ? new Date(invoice.created_at) : null;
  const timePart = createdAt && !Number.isNaN(createdAt.getTime())
    ? createdAt.toLocaleTimeString("es-NI", { hour: "2-digit", minute: "2-digit" })
    : "";
  return `${datePart} ${timePart}`.trim();
}

async function loadInvoices() {
  loading.value = true;
  try {
    invoices.value = await fetchSalesInvoices(filters);
  } catch (error) {
    toast.add({ severity: "error", summary: "No se cargaron facturas", detail: error.message, life: 3500 });
  } finally {
    loading.value = false;
  }
}

function resetToday() {
  filters.q = "";
  filters.start_date = today;
  filters.end_date = today;
  filters.status_filter = "TODAS";
  loadInvoices();
}

async function loadPrintPayload(invoice) {
  printPayload.value = await fetchSalesInvoicePrint(invoice.id);
}

async function openDetail(invoice) {
  try {
    selectedInvoice.value = invoice;
    await loadPrintPayload(invoice);
    detailDialog.value = true;
  } catch (error) {
    toast.add({ severity: "error", summary: "No se cargo el detalle", detail: error.message, life: 3500 });
  }
}

async function openPrint(invoice, format) {
  if (!canReprint.value) return;
  try {
    selectedInvoice.value = invoice;
    printFormat.value = format;
    await loadPrintPayload(invoice);
    printDialog.value = true;
  } catch (error) {
    toast.add({ severity: "error", summary: "No se preparo la reimpresion", detail: error.message, life: 3500 });
  }
}

function printInvoice() {
  document.body.classList.add("printing-sales-invoice");
  window.print();
  window.setTimeout(() => document.body.classList.remove("printing-sales-invoice"), 500);
}

function openVoidDialog(invoice) {
  if (!canVoid.value || isVoided(invoice)) return;
  selectedInvoice.value = invoice;
  voidReason.value = "";
  voidDialog.value = true;
}

async function confirmVoid() {
  if (!selectedInvoice.value) return;
  voiding.value = true;
  try {
    await voidSalesInvoice(selectedInvoice.value.id, {
      motivo: voidReason.value,
      usuario_registro: currentUser.value.full_name || currentUser.value.username || "Usuario",
    });
    toast.add({ severity: "success", summary: "Factura anulada", detail: "Inventario devuelto automaticamente.", life: 2800 });
    voidDialog.value = false;
    await loadInvoices();
  } catch (error) {
    toast.add({ severity: "error", summary: "No se pudo anular", detail: error.message, life: 4200 });
  } finally {
    voiding.value = false;
  }
}

async function hydrateCurrentUser() {
  try {
    currentUser.value = await fetchCurrentUser();
    localStorage.setItem("currentUser", JSON.stringify(currentUser.value));
  } catch {
    currentUser.value = readStoredUser() || {};
  }
}

onMounted(async () => {
  await hydrateCurrentUser();
  await loadInvoices();
});
</script>

<style scoped>
.sales-utilities-page {
  display: grid;
  gap: 1rem;
}

.sales-utilities-header {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
}

.utilities-caption {
  color: var(--erp-text-soft);
  margin: 0.35rem 0 0;
}

.utilities-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(92px, 1fr));
  gap: 0.65rem;
  min-width: min(420px, 100%);
}

.utilities-stats article,
.utilities-summary,
.void-box {
  border: 1px solid var(--erp-border);
  border-radius: 8px;
  background: #fff;
}

.utilities-stats article {
  padding: 0.85rem;
}

.utilities-stats span,
.utilities-summary span,
.void-box span {
  display: block;
  color: var(--erp-text-soft);
  font-size: 0.72rem;
  text-transform: uppercase;
  font-weight: 800;
}

.utilities-stats strong {
  display: block;
  font-size: 1.35rem;
}

.utilities-filter-grid {
  display: grid;
  grid-template-columns: minmax(260px, 1.7fr) repeat(3, minmax(140px, 0.8fr)) auto;
  gap: 0.75rem;
  align-items: end;
}

.utilities-filter-actions,
.utilities-row-actions,
.print-toolbar {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.utilities-row-actions {
  flex-wrap: wrap;
}

.invoice-link {
  border: 0;
  background: transparent;
  color: var(--erp-primary);
  font-weight: 800;
  padding: 0;
}

.utilities-detail-grid {
  display: grid;
  grid-template-columns: minmax(220px, 0.8fr) minmax(0, 1.4fr);
  gap: 1rem;
}

.utilities-summary,
.void-box {
  padding: 1rem;
  display: grid;
  gap: 0.75rem;
}

.void-box {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.print-preview-shell {
  display: grid;
  gap: 1rem;
}

.print-toolbar {
  justify-content: space-between;
}

.invoice-print-area {
  background: #fff;
  color: #111827;
  border: 1px solid #d6dee9;
  padding: 1rem;
  margin: 0 auto;
  position: relative;
}

.invoice-print-pos {
  width: 302px;
  font-size: 11px;
}

.invoice-print-letter {
  width: min(760px, 100%);
  min-height: 920px;
  font-size: 13px;
}

.invoice-print-head {
  text-align: center;
  border-bottom: 1px dashed #9ca3af;
  padding-bottom: 0.6rem;
  margin-bottom: 0.65rem;
}

.invoice-print-head img {
  max-width: 120px;
  max-height: 56px;
  object-fit: contain;
  margin-bottom: 0.35rem;
}

.invoice-print-head h2,
.invoice-print-head p {
  margin: 0.1rem 0;
}

.invoice-print-meta {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.35rem 0.8rem;
  margin-bottom: 0.8rem;
}

.invoice-print-meta span {
  display: block;
  color: #64748b;
  font-size: 0.7em;
  text-transform: uppercase;
  font-weight: 800;
}

.invoice-print-table {
  width: 100%;
  border-collapse: collapse;
}

.invoice-print-table th,
.invoice-print-table td {
  border-bottom: 1px solid #e5e7eb;
  padding: 0.35rem 0.25rem;
  vertical-align: top;
}

.invoice-print-table td span {
  display: block;
  color: #475569;
}

.num {
  text-align: right;
  white-space: nowrap;
}

.invoice-print-totals {
  margin-left: auto;
  margin-top: 0.8rem;
  width: min(280px, 100%);
  display: grid;
  gap: 0.25rem;
}

.invoice-print-totals div {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.invoice-void-watermark {
  margin: 1rem 0 0;
  text-align: center;
  color: #b91c1c;
  font-weight: 900;
  border: 2px solid #b91c1c;
  padding: 0.45rem;
}

@media (max-width: 920px) {
  .sales-utilities-header,
  .utilities-detail-grid {
    grid-template-columns: 1fr;
    display: grid;
  }

  .utilities-filter-grid {
    grid-template-columns: 1fr 1fr;
  }

  .utilities-search,
  .utilities-filter-actions {
    grid-column: 1 / -1;
  }
}

@media print {
  :global(body.printing-sales-invoice *) {
    visibility: hidden !important;
  }

  :global(body.printing-sales-invoice .invoice-print-area),
  :global(body.printing-sales-invoice .invoice-print-area *) {
    visibility: visible !important;
  }

  :global(body.printing-sales-invoice .invoice-print-area) {
    position: fixed;
    inset: 0 auto auto 0;
    border: 0;
    margin: 0;
    box-shadow: none;
  }
}
</style>
