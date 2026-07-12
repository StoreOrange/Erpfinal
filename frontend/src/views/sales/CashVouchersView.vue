<!--
  Vales de caja.
  Hecho por Carlos.
  Colaboracion academica: Oded Garcia y Carlos Ramirez.
  Recordatorio: clasificar bien ingresos y egresos para no afectar caja.
-->
<template>
  <section class="page-section cash-vouchers-page">
    <header class="module-hero">
      <div class="module-hero-copy">
        <p class="page-kicker">Ventas y Facturacion</p>
        <h1 class="page-title">Vales de Caja</h1>
        <p class="panel-text">Registra ingresos y egresos que afectan automaticamente el cierre de caja diario.</p>
      </div>
      <div class="module-hero-meta">
        <div class="module-meta-box">
          <span>Fecha</span>
          <strong>{{ form.fecha }}</strong>
        </div>
        <div class="module-meta-box">
          <span>Tasa</span>
          <strong>C$ {{ formatMoney(exchangeRate) }}</strong>
        </div>
        <div class="module-meta-box">
          <span>Total C$</span>
          <strong>C$ {{ formatMoney(voucherTotalCs) }}</strong>
        </div>
      </div>
    </header>

    <div v-if="alert.message" class="settings-feedback" :class="alert.type === 'success' ? 'settings-feedback-success' : 'settings-feedback-error'">
      <i class="bi" :class="alert.type === 'success' ? 'bi-check-circle-fill' : 'bi-exclamation-circle-fill'"></i>
      <span>{{ alert.message }}</span>
    </div>

    <div class="cash-voucher-layout">
      <article class="panel-card cash-voucher-form-card">
        <div class="panel-head">
          <div>
            <span class="products-section-kicker">Nuevo vale</span>
            <h3>Recibo oficial de caja</h3>
          </div>
          <Tag :severity="form.tipo === 'INGRESO' ? 'success' : 'danger'" :value="form.tipo" />
        </div>

        <form class="cash-voucher-form" @submit.prevent="submitVoucher">
          <div class="cash-voucher-typebar">
            <button type="button" :class="{ active: form.tipo === 'INGRESO' }" @click="setMovementType('INGRESO')">
              <i class="bi bi-arrow-down-circle"></i>
              Ingreso
            </button>
            <button type="button" :class="{ active: form.tipo === 'EGRESO' }" @click="setMovementType('EGRESO')">
              <i class="bi bi-arrow-up-circle"></i>
              Egreso
            </button>
          </div>

          <div class="product-form-grid">
            <label class="field-group">
              <span>Fecha</span>
              <input v-model="form.fecha" class="form-control" type="date" />
            </label>
            <label class="field-group">
              <span>Bodega</span>
              <select v-model="form.bodega_id" class="form-control">
                <option :value="null">Todas</option>
                <option v-for="bodega in bodegas" :key="bodega.id" :value="bodega.id">{{ bodega.name }}</option>
              </select>
            </label>
            <label class="field-group">
              <span>Moneda</span>
              <select v-model="form.moneda" class="form-control">
                <option value="CS">Cordobas</option>
                <option value="USD">Dolares</option>
              </select>
            </label>
            <label class="field-group">
              <span>Monto</span>
              <input v-model="form.monto" class="form-control" inputmode="decimal" placeholder="0.00" @input="normalizeMoneyInput" />
            </label>
            <label class="field-group">
              <span>Rubro</span>
              <select v-model="form.rubro" class="form-control">
                <option value="">Selecciona tipo de {{ form.tipo === "EGRESO" ? "gasto" : "ingreso" }}</option>
                <option v-for="rubro in filteredRubros" :key="rubro" :value="rubro">{{ rubro }}</option>
              </select>
            </label>
            <label class="field-group">
              <span>{{ motivoLabel }}</span>
              <select v-model="form.motivo" class="form-control cash-voucher-motive-select">
                <option value="">Selecciona el tipo de movimiento</option>
                <option v-for="motivo in filteredMotivos" :key="motivo" :value="motivo">{{ motivo }}</option>
              </select>
            </label>
            <label class="field-group field-span-2">
              <span>Descripcion</span>
              <textarea v-model.trim="form.descripcion" class="form-control cash-voucher-textarea" placeholder="Observacion para el recibo POS"></textarea>
            </label>
          </div>

          <div class="cash-voucher-summary">
            <div>
              <span>Monto original</span>
              <strong>{{ form.moneda === "USD" ? "US$" : "C$" }} {{ formatMoney(form.monto) }}</strong>
            </div>
            <div>
              <span>Equivalente C$</span>
              <strong>C$ {{ formatMoney(formAmountCs) }}</strong>
            </div>
            <label class="cash-voucher-check">
              <input v-model="form.afecta_caja" type="checkbox" />
              <span>Afecta arqueo de caja</span>
            </label>
          </div>

          <div class="cash-voucher-accounting">
            <h4>Mini asiento contable</h4>
            <div v-if="form.tipo === 'EGRESO'" class="cash-voucher-accounting-lines">
              <div><span>Debe</span><strong>{{ form.rubro || "Rubro del gasto" }}</strong></div>
              <div><span>Haber</span><strong>1101 Caja</strong></div>
            </div>
            <div v-else class="cash-voucher-accounting-lines">
              <div><span>Debe</span><strong>1101 Caja</strong></div>
              <div><span>Haber</span><strong>{{ form.rubro || "Rubro del ingreso" }}</strong></div>
            </div>
          </div>

          <div class="product-form-actions">
            <Button type="button" severity="secondary" variant="outlined" label="Limpiar" @click="resetForm" />
            <Button type="submit" icon="bi bi-save2" :disabled="saving" :label="saving ? 'Guardando...' : 'Registrar vale'" />
          </div>
        </form>
      </article>

      <article class="panel-card cash-voucher-history-card">
        <div class="panel-head">
          <div>
            <span class="products-section-kicker">Historico</span>
            <h3>Vales registrados</h3>
          </div>
          <Button type="button" severity="secondary" variant="outlined" icon="bi bi-arrow-clockwise" label="Actualizar" @click="loadVouchers" />
        </div>

        <div class="cash-voucher-filters">
          <label class="field-group">
            <span>Desde</span>
            <input v-model="filters.startDate" class="form-control" type="date" />
          </label>
          <label class="field-group">
            <span>Hasta</span>
            <input v-model="filters.endDate" class="form-control" type="date" />
          </label>
          <Button type="button" icon="bi bi-filter" label="Filtrar" @click="loadVouchers" />
        </div>

        <div class="cash-voucher-list">
          <article v-for="voucher in vouchers" :key="voucher.id" class="cash-voucher-row">
            <div>
              <strong>{{ voucher.numero }} - {{ voucher.tipo }}</strong>
              <span>{{ voucher.fecha }} - {{ voucher.rubro }} - {{ voucher.motivo }}</span>
            </div>
            <b :class="voucher.tipo === 'INGRESO' ? 'positive' : 'negative'">
              {{ voucher.tipo === "INGRESO" ? "+" : "-" }} C$ {{ formatMoney(voucher.monto_cs) }}
            </b>
            <Button type="button" severity="secondary" variant="text" rounded icon="bi bi-printer" @click="selectReceipt(voucher)" />
          </article>
          <div v-if="!vouchers.length" class="empty-state">No hay vales de caja para el filtro seleccionado.</div>
        </div>
      </article>
    </div>

    <article v-if="selectedReceipt" class="panel-card cash-voucher-receipt-card">
      <div class="panel-head">
        <div>
          <span class="products-section-kicker">Recibo POS</span>
          <h3>{{ selectedReceipt.numero }}</h3>
        </div>
        <Button type="button" icon="bi bi-printer" label="Imprimir recibo" @click="printReceipt" />
      </div>
      <div class="cash-voucher-receipt-print">
        <div class="receipt-center">
          <h3>Recibo oficial de caja</h3>
          <p>{{ selectedReceipt.numero }}</p>
          <p>{{ selectedReceipt.fecha }} - {{ receiptTimeLabel(selectedReceipt) }}</p>
          <p>{{ selectedBodegaName(selectedReceipt.bodega_id) }}</p>
        </div>
        <hr />
        <div class="receipt-lines">
          <div><span>Tipo</span><strong>{{ selectedReceipt.tipo }}</strong></div>
          <div><span>Rubro</span><strong>{{ selectedReceipt.rubro }}</strong></div>
          <div><span>Motivo</span><strong>{{ selectedReceipt.motivo }}</strong></div>
          <div><span>Monto</span><strong>{{ selectedReceipt.moneda === "USD" ? "US$" : "C$" }} {{ formatMoney(originalAmount(selectedReceipt)) }}</strong></div>
          <div><span>Equiv. C$</span><strong>C$ {{ formatMoney(selectedReceipt.monto_cs) }}</strong></div>
          <div><span>Afecta caja</span><strong>{{ selectedReceipt.afecta_caja ? "Si" : "No" }}</strong></div>
        </div>
        <hr />
        <h4>Detalle</h4>
        <p class="receipt-note">{{ selectedReceipt.descripcion || "-" }}</p>
        <hr />
        <h4>Mini asiento</h4>
        <div class="receipt-lines">
          <template v-if="selectedReceipt.tipo === 'EGRESO'">
            <div><span>Debe</span><strong>{{ selectedReceipt.rubro }}</strong></div>
            <div><span>Haber</span><strong>1101 Caja</strong></div>
          </template>
          <template v-else>
            <div><span>Debe</span><strong>1101 Caja</strong></div>
            <div><span>Haber</span><strong>{{ selectedReceipt.rubro }}</strong></div>
          </template>
        </div>
        <div class="receipt-signature"><span>Firma responsable</span></div>
      </div>
    </article>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import Button from "primevue/button";
import Tag from "primevue/tag";

import { fetchInventoryCatalogs } from "../../services/inventory";
import { createCashVoucher, fetchCashVouchers } from "../../services/sales";
import { readStoredUser } from "../../services/auth";
import { fetchCurrentExchangeRate } from "../../services/settings";

const today = new Date().toISOString().slice(0, 10);
const currentUser = readStoredUser();
const exchangeRate = ref(0);
const bodegas = ref([]);
const vouchers = ref([]);
const selectedReceipt = ref(null);
const saving = ref(false);
const alert = reactive({ type: "", message: "" });
const filters = reactive({ startDate: today, endDate: today });
const form = reactive({
  fecha: today,
  bodega_id: null,
  tipo: "EGRESO",
  rubro: "",
  motivo: "",
  descripcion: "",
  moneda: "CS",
  monto: "",
  afecta_caja: true,
});

const rubrosCatalog = {
  EGRESO: [
    "Transporte",
    "Fletes y acarreo",
    "Combustible",
    "Compras varias",
    "Compra de insumos",
    "Compra de mercaderia",
    "Materiales de empaque",
    "Materiales de limpieza",
    "Papeleria y utiles",
    "Alimentacion y viaticos",
    "Servicios basicos",
    "Alquiler",
    "Mantenimiento y reparaciones",
    "Seguridad",
    "Gastos administrativos",
    "Gastos de venta",
    "Otros gastos",
  ],
  INGRESO: [
    "Venta de productos",
    "Abono de cliente",
    "Anticipo de cliente",
    "Recuperacion de credito",
    "Aporte de socio",
    "Ajuste positivo de caja",
    "Otros ingresos",
  ],
};

const motivosCatalog = {
  EGRESO: [
    "Transporte",
    "Fletes y acarreo",
    "Combustible",
    "Compras varias",
    "Compra de insumos",
    "Compra de mercaderia",
    "Compra de articulos de limpieza",
    "Compra de materiales de limpieza",
    "Viaticos",
    "Mantenimiento",
    "Reparaciones",
    "Alquiler",
    "Fletes",
    "Pago de servicios basicos",
    "Gastos de papeleria",
    "Gastos de ventas",
    "Pago por servicios de seguridad",
    "Otros gastos",
  ],
  INGRESO: ["Venta de productos", "Abono de cliente", "Anticipo recibido", "Aporte de socio", "Otros ingresos"],
};

const formAmount = computed(() => Number(form.monto || 0));
const formAmountCs = computed(() => (form.moneda === "USD" ? formAmount.value * Number(exchangeRate.value || 0) : formAmount.value));
const voucherTotalCs = computed(() =>
  vouchers.value.reduce((total, voucher) => total + (voucher.tipo === "INGRESO" ? 1 : -1) * Number(voucher.monto_cs || 0), 0),
);
const filteredRubros = computed(() => rubrosCatalog[form.tipo] || []);
const filteredMotivos = computed(() => motivosCatalog[form.tipo] || []);
const motivoLabel = computed(() => (form.tipo === "EGRESO" ? "Tipo de egreso" : "Tipo de ingreso"));

function formatMoney(value) {
  return new Intl.NumberFormat("es-NI", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(Number(value || 0));
}

function normalizeMoneyInput() {
  const raw = String(form.monto || "").replace(/[^0-9.]/g, "");
  const [integer, ...decimals] = raw.split(".");
  form.monto = decimals.length ? `${integer}.${decimals.join("").slice(0, 2)}` : integer;
}

function showAlert(type, message) {
  alert.type = type;
  alert.message = message;
  window.setTimeout(() => {
    if (alert.message === message) alert.message = "";
  }, 3500);
}

function resetForm() {
  form.tipo = "EGRESO";
  form.rubro = "";
  form.motivo = "";
  form.descripcion = "";
  form.moneda = "CS";
  form.monto = "";
  form.afecta_caja = true;
}

function setMovementType(tipo) {
  if (form.tipo === tipo) return;
  form.tipo = tipo;
  form.rubro = "";
  form.motivo = "";
}

async function loadExchangeRate() {
  try {
    const currentRate = await fetchCurrentExchangeRate();
    exchangeRate.value = currentRate?.rate ? Number(currentRate.rate) : 0;
  } catch {
    exchangeRate.value = 0;
  }
}

async function loadCatalogs() {
  try {
    const catalogs = await fetchInventoryCatalogs();
    bodegas.value = catalogs.bodegas || [];
  } catch {
    bodegas.value = [];
  }
}

async function loadVouchers() {
  try {
    vouchers.value = await fetchCashVouchers(filters.startDate, filters.endDate);
  } catch (error) {
    showAlert("error", error.message || "No se pudieron cargar los vales de caja.");
  }
}

async function submitVoucher() {
  if (!form.rubro || !form.motivo || formAmount.value <= 0) {
    showAlert("error", "Completa rubro, motivo y monto valido.");
    return;
  }
  if (form.moneda === "USD" && Number(exchangeRate.value || 0) <= 0) {
    showAlert("error", "Registra una tasa de cambio vigente para vales en dolares.");
    return;
  }
  saving.value = true;
  try {
    const voucher = await createCashVoucher({
      ...form,
      bodega_id: form.bodega_id ? Number(form.bodega_id) : null,
      monto: formAmount.value,
      tasa_cambio: Number(exchangeRate.value || 0) > 0 ? Number(exchangeRate.value || 0) : null,
      usuario_registro: currentUser?.email || currentUser?.full_name || "sistema",
    });
    selectedReceipt.value = voucher;
    resetForm();
    await loadVouchers();
    showAlert("success", `${voucher.numero} registrado correctamente.`);
  } catch (error) {
    showAlert("error", error.message || "No se pudo registrar el vale de caja.");
  } finally {
    saving.value = false;
  }
}

function selectedBodegaName(bodegaId) {
  const selected = bodegas.value.find((item) => Number(item.id) === Number(bodegaId));
  return selected?.name || "Todas las bodegas";
}

function originalAmount(voucher) {
  return voucher.moneda === "USD" ? Number(voucher.monto_usd || 0) : Number(voucher.monto_cs || 0);
}

function receiptTimeLabel(voucher) {
  if (!voucher.created_at) return "";
  return new Intl.DateTimeFormat("es-NI", { hour: "2-digit", minute: "2-digit" }).format(new Date(voucher.created_at));
}

function selectReceipt(voucher) {
  selectedReceipt.value = voucher;
}

function printReceipt() {
  document.body.classList.add("printing-cash-voucher-receipt");
  window.print();
  window.setTimeout(() => document.body.classList.remove("printing-cash-voucher-receipt"), 500);
}

onMounted(async () => {
  await Promise.all([loadExchangeRate(), loadCatalogs(), loadVouchers()]);
});
</script>

<style scoped>
.cash-vouchers-page,
.cash-voucher-form,
.cash-voucher-form-card,
.cash-voucher-history-card {
  display: grid;
  gap: 1rem;
}

.cash-voucher-layout {
  display: grid;
  grid-template-columns: minmax(24rem, 0.8fr) minmax(0, 1.2fr);
  gap: 1rem;
  align-items: start;
}

.cash-voucher-typebar {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.5rem;
}

.cash-voucher-typebar button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  min-height: 2.65rem;
  border: 1px solid var(--erp-line);
  border-radius: 8px;
  background: var(--erp-surface-muted);
  color: var(--erp-text);
  font-weight: 800;
}

.cash-voucher-typebar button.active {
  border-color: var(--erp-primary);
  background: var(--erp-primary);
  color: #fff;
}

.cash-voucher-textarea {
  min-height: 5rem;
  resize: vertical;
}

.cash-voucher-motive-select {
  border-color: var(--erp-primary);
  font-weight: 800;
}

.cash-voucher-form .product-form-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.cash-voucher-form .field-span-2 {
  grid-column: 1 / -1;
}

.cash-voucher-summary,
.cash-voucher-filters {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.65rem;
}

.cash-voucher-summary > div,
.cash-voucher-check,
.cash-voucher-accounting {
  padding: 0.75rem;
  border: 1px solid var(--erp-line);
  border-radius: 8px;
  background: var(--erp-surface-muted);
}

.cash-voucher-summary span,
.cash-voucher-accounting span,
.cash-voucher-row span {
  display: block;
  color: var(--erp-text-muted);
  font-size: 0.72rem;
  font-weight: 800;
  text-transform: uppercase;
}

.cash-voucher-check {
  display: flex;
  align-items: center;
  gap: 0.55rem;
}

.cash-voucher-accounting h4 {
  margin: 0 0 0.65rem;
  font-size: 0.9rem;
}

.cash-voucher-accounting-lines,
.cash-voucher-list {
  display: grid;
  gap: 0.5rem;
}

.cash-voucher-accounting-lines div,
.cash-voucher-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto auto;
  align-items: center;
  gap: 0.65rem;
}

.cash-voucher-row {
  padding: 0.75rem;
  border: 1px solid var(--erp-line);
  border-radius: 8px;
  background: var(--erp-surface-muted);
}

.cash-voucher-receipt-print {
  max-width: 22rem;
  padding: 1rem;
  border: 1px dashed var(--erp-line-strong);
  background: #fff;
  color: #111;
  font-family: "Courier New", Courier, monospace;
  font-size: 0.82rem;
  line-height: 1.35;
}

.receipt-center {
  text-align: center;
}

.receipt-center h3,
.receipt-center p,
.cash-voucher-receipt-print h4,
.receipt-note {
  margin: 0;
}

.cash-voucher-receipt-print h4 {
  font-size: 0.82rem;
  text-transform: uppercase;
}

.cash-voucher-receipt-print hr {
  margin: 0.55rem 0;
  border: 0;
  border-top: 1px dashed #222;
}

.receipt-lines {
  display: grid;
  gap: 0.2rem;
}

.receipt-lines div {
  display: flex;
  justify-content: space-between;
  gap: 0.65rem;
}

.receipt-lines strong {
  text-align: right;
  white-space: nowrap;
}

.receipt-signature {
  margin-top: 2rem;
  padding-top: 0.35rem;
  border-top: 1px solid #111;
  text-align: center;
}

.positive {
  color: var(--erp-success);
}

.negative {
  color: var(--erp-danger);
}

.cash-close-voucher-link,
.cash-voucher-row .p-button {
  white-space: nowrap;
}

@media print {
  :global(body.printing-cash-voucher-receipt *) {
    visibility: hidden !important;
  }

  :global(body.printing-cash-voucher-receipt .cash-voucher-receipt-print),
  :global(body.printing-cash-voucher-receipt .cash-voucher-receipt-print *) {
    visibility: visible !important;
  }

  :global(body.printing-cash-voucher-receipt .cash-voucher-receipt-print) {
    position: fixed;
    top: 0;
    left: 0;
    width: 80mm;
    max-width: 80mm;
    border: 0;
    box-shadow: none;
  }
}

@media (max-width: 980px) {
  .cash-voucher-layout,
  .cash-voucher-form .product-form-grid,
  .cash-voucher-summary,
  .cash-voucher-filters {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
