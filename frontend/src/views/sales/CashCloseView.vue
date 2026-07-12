<!--
  Cierre de caja diario.
  Hecho por Carlos.
  Colaboracion academica: Oded Garcia y Carlos Ramirez.
  Nota: esta pantalla resume ventas, efectivo y diferencias de caja.
-->
<template>
  <section class="page-section cash-close-page">
    <div v-if="alert.message" class="settings-feedback" :class="alert.type === 'success' ? 'settings-feedback-success' : 'settings-feedback-error'">
      <i class="bi" :class="alert.type === 'success' ? 'bi-check-circle-fill' : 'bi-exclamation-circle-fill'"></i>
      <span>{{ alert.message }}</span>
    </div>

    <div class="cash-close-layout">
      <article class="panel-card cash-count-panel">
        <div class="panel-head">
          <div>
            <span class="products-section-kicker">Cierre de caja</span>
            <h3>Desglose de denominaciones</h3>
          </div>
        </div>

        <div class="cash-close-controls">
          <label class="field-group cash-close-compact-field cash-close-date-field">
            <span>Fecha</span>
            <input v-model="closeDate" class="form-control" type="date" @change="loadSummary" />
          </label>
          <label class="field-group cash-close-compact-field cash-close-bodega-field">
            <span>Bodega</span>
            <select v-model="bodegaId" class="form-control" @change="loadSummary">
              <option :value="null">Todas</option>
              <option v-for="bodega in bodegas" :key="bodega.id" :value="bodega.id">{{ bodega.name }}</option>
            </select>
          </label>
          <label class="field-group cash-close-compact-field cash-close-rate-field">
            <span>Tasa de cambio</span>
            <input v-model.number="exchangeRate" class="form-control" type="number" min="0" step="0.0001" />
          </label>
        </div>

        <div class="cash-denomination-grid">
          <section class="cash-denomination-card">
            <div class="cash-denomination-head">
              <div>
                <span>Cordobas</span>
                <h4>C$ {{ formatMoney(totalCordobas) }}</h4>
              </div>
              <i class="bi bi-cash-stack"></i>
            </div>
            <div class="cash-denomination-table">
              <div class="cash-denomination-row cash-denomination-row-head">
                <span>Denom</span>
                <span>Cant.</span>
                <span>Total</span>
              </div>
              <div v-for="item in cordobaDenominations" :key="item.value" class="cash-denomination-row">
                <span>C$ {{ formatDenomination(item.value) }}</span>
                <input
                  v-model="item.quantity"
                  class="form-control"
                  type="text"
                  inputmode="numeric"
                  pattern="[0-9]*"
                  @input="normalizeDenominationQuantity(item)"
                />
                <strong>C$ {{ formatMoney(denominationTotal(item)) }}</strong>
              </div>
            </div>
          </section>

          <section class="cash-denomination-card">
            <div class="cash-denomination-head">
              <div>
                <span>Dolares</span>
                <h4>US$ {{ formatMoney(totalDollars) }}</h4>
              </div>
              <i class="bi bi-currency-dollar"></i>
            </div>
            <div class="cash-denomination-table">
              <div class="cash-denomination-row cash-denomination-row-head">
                <span>Denom</span>
                <span>Cant.</span>
                <span>Total</span>
              </div>
              <div v-for="item in dollarDenominations" :key="item.value" class="cash-denomination-row">
                <span>US$ {{ formatDenomination(item.value) }}</span>
                <input
                  v-model="item.quantity"
                  class="form-control"
                  type="text"
                  inputmode="numeric"
                  pattern="[0-9]*"
                  @input="normalizeDenominationQuantity(item)"
                />
                <strong>US$ {{ formatMoney(denominationTotal(item)) }}</strong>
              </div>
            </div>
          </section>
        </div>

        <div class="cash-close-totals">
          <div><span>Total C$ contado</span><strong>C$ {{ formatMoney(totalCordobas) }}</strong></div>
          <div><span>Total USD contado</span><strong>US$ {{ formatMoney(totalDollars) }}</strong></div>
          <div><span>USD en C$</span><strong>C$ {{ formatMoney(totalDollarsInCordobas) }}</strong></div>
          <div><span>Efectivo fisico C$</span><strong>C$ {{ formatMoney(cashCounted) }}</strong></div>
        </div>

        <div class="product-form-actions">
          <Button type="button" icon="bi bi-check2-circle" :disabled="saving || summary.has_closed" :label="summary.has_closed ? 'Cierre ya registrado' : saving ? 'Registrando...' : 'Registrar cierre'" @click="submitClose" />
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import Button from "primevue/button";

import { fetchInventoryCatalogs } from "../../services/inventory";
import { createCashClose, fetchCashCloseSummary } from "../../services/sales";
import { readStoredUser } from "../../services/auth";
import { fetchCurrentExchangeRate } from "../../services/settings";

const currentUser = readStoredUser();
const closeDate = ref(new Date().toISOString().slice(0, 10));
const bodegaId = ref(null);
const exchangeRate = ref(0);
const observation = ref("");
const saving = ref(false);
const summary = ref({});
const bodegas = ref([]);
const lastClose = ref(null);
const alert = reactive({ type: "", message: "" });
const cordobaDenominations = reactive([1000, 500, 200, 100, 50, 20, 10, 5, 1, 0.5].map((value) => ({ value, quantity: 0 })));
const dollarDenominations = reactive([100, 50, 20, 10, 5, 2, 1].map((value) => ({ value, quantity: 0 })));

const incomeTotal = computed(() => Number(summary.value.ingresos_caja_cs || 0));
const expenseTotal = computed(() => Number(summary.value.egresos_caja_cs || 0));
const totalCordobas = computed(() => cordobaDenominations.reduce((total, item) => total + denominationTotal(item), 0));
const totalDollars = computed(() => dollarDenominations.reduce((total, item) => total + denominationTotal(item), 0));
const totalDollarsInCordobas = computed(() => totalDollars.value * Number(exchangeRate.value || 0));
const cashCounted = computed(() => totalCordobas.value + totalDollarsInCordobas.value);
const expectedCash = computed(() => Number(summary.value.efectivo_ventas_cs || 0) + incomeTotal.value - expenseTotal.value);
const difference = computed(() => Number(cashCounted.value || 0) - expectedCash.value);
const resultLabel = computed(() => {
  if (difference.value > 0.009) return "Sobrante";
  if (difference.value < -0.009) return "Faltante";
  return "Cuadrado";
});
const resultSeverity = computed(() => {
  if (difference.value > 0.009) return "info";
  if (difference.value < -0.009) return "danger";
  return "success";
});
const differenceClass = computed(() => ({
  positive: difference.value > 0.009,
  negative: difference.value < -0.009,
}));
const selectedBodegaName = computed(() => {
  if (summary.value.bodega_name) return summary.value.bodega_name;
  const selected = bodegas.value.find((item) => Number(item.id) === Number(bodegaId.value));
  return selected?.name || "Todas las bodegas";
});
const receiptInvoiceCount = computed(() => summary.value.invoice_count || 0);
const closeTimeLabel = computed(() =>
  new Intl.DateTimeFormat("es-NI", { hour: "2-digit", minute: "2-digit" }).format(new Date()),
);
const receiptCordobaDetails = computed(() => parseCashDetail(lastClose.value?.detalle_cs));
const receiptDollarDetails = computed(() => parseCashDetail(lastClose.value?.detalle_usd));

function formatMoney(value) {
  return new Intl.NumberFormat("es-NI", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(Number(value || 0));
}

function formatDenomination(value) {
  return Number(value) % 1 === 0 ? String(Number(value)) : formatMoney(value);
}

function denominationTotal(item) {
  return Number(item.value || 0) * Number(item.quantity || 0);
}

function normalizeDenominationQuantity(item) {
  const digits = String(item.quantity ?? "").replace(/\D/g, "");
  item.quantity = digits ? Number(digits) : 0;
}

function denominationPayload(items) {
  return items.reduce((payload, item) => {
    payload[String(item.value)] = Number(item.quantity || 0);
    return payload;
  }, {});
}

function parseCashDetail(rawDetail) {
  if (!rawDetail) return [];
  let detail = rawDetail;
  if (typeof rawDetail === "string") {
    try {
      detail = JSON.parse(rawDetail);
    } catch {
      detail = {};
    }
  }
  return Object.entries(detail)
    .map(([denom, quantity]) => ({
      denom: Number(denom || 0),
      quantity: Number(quantity || 0),
      total: Number(denom || 0) * Number(quantity || 0),
    }))
    .filter((item) => item.denom > 0 && item.quantity > 0)
    .sort((a, b) => b.denom - a.denom);
}

function showAlert(type, message) {
  alert.type = type;
  alert.message = message;
  window.setTimeout(() => {
    if (alert.message === message) alert.message = "";
  }, 3500);
}

async function loadSummary() {
  try {
    summary.value = await fetchCashCloseSummary(closeDate.value, bodegaId.value);
  } catch (error) {
    showAlert("error", error.message || "No se pudo cargar el resumen de caja.");
  }
}

async function loadExchangeRate() {
  try {
    const currentRate = await fetchCurrentExchangeRate();
    exchangeRate.value = currentRate?.rate ? Number(currentRate.rate) : 0;
  } catch {
    exchangeRate.value = 0;
  }
}

async function submitClose() {
  if (totalDollars.value > 0 && Number(exchangeRate.value || 0) <= 0) {
    showAlert("error", "Registra una tasa de cambio para convertir los dolares a cordobas.");
    return;
  }
  saving.value = true;
  try {
    const close = await createCashClose({
      fecha: closeDate.value,
      bodega_id: bodegaId.value ? Number(bodegaId.value) : null,
      efectivo_fisico_cs: Number(cashCounted.value || 0),
      detalle_cs: denominationPayload(cordobaDenominations),
      detalle_usd: denominationPayload(dollarDenominations),
      total_efectivo_cs: Number(totalCordobas.value || 0),
      total_efectivo_usd: Number(totalDollars.value || 0),
      tasa_cambio: Number(exchangeRate.value || 0) > 0 ? Number(exchangeRate.value || 0) : null,
      observacion: observation.value,
      usuario_registro: currentUser?.email || currentUser?.full_name || "sistema",
      movements: [],
    });
    lastClose.value = close;
    showAlert("success", `${close.cierre_numero} registrado correctamente.`);
    await loadSummary();
  } catch (error) {
    showAlert("error", error.message || "No se pudo cerrar caja.");
  } finally {
    saving.value = false;
  }
}

function printClose() {
  document.body.classList.add("printing-cash-close");
  window.print();
  window.setTimeout(() => document.body.classList.remove("printing-cash-close"), 500);
}

onMounted(async () => {
  try {
    const catalogs = await fetchInventoryCatalogs();
    bodegas.value = catalogs.bodegas || [];
  } catch {
    bodegas.value = [];
  }
  await Promise.all([loadExchangeRate(), loadSummary()]);
});
</script>

<style scoped>
.cash-close-page,
.cash-close-panel {
  display: grid;
  gap: 1rem;
}

.cash-close-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(22rem, 0.36fr);
  gap: 1rem;
  align-items: start;
}

.cash-close-main-panel,
.cash-count-panel {
  grid-column: 1 / -1;
}

.cash-count-panel {
  display: grid;
  gap: 1rem;
}

.cash-close-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: end;
}

.cash-close-compact-field {
  flex: 0 0 auto;
  min-width: 0;
}

.cash-close-date-field {
  width: 12rem;
}

.cash-close-bodega-field {
  width: 16rem;
}

.cash-close-rate-field {
  width: 11rem;
}

.cash-close-compact-field .form-control {
  width: 100%;
}

.cash-movements-panel {
  grid-column: 1 / -1;
}

.cash-close-kpis,
.cash-close-totals {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.65rem;
}

.cash-close-kpis div,
.cash-close-totals div,
.cash-movement-row {
  padding: 0.75rem;
  border: 1px solid var(--erp-line);
  border-radius: 8px;
  background: var(--erp-surface-muted);
}

.cash-close-kpis span,
.cash-close-totals span,
.cash-movement-row span {
  display: block;
  color: var(--erp-text-muted);
  font-size: 0.72rem;
  font-weight: 800;
  text-transform: uppercase;
}

.cash-close-kpis strong,
.cash-close-totals strong {
  display: block;
  margin-top: 0.25rem;
}

.cash-rate-pill {
  display: inline-grid;
  gap: 0.1rem;
  min-width: 7rem;
  padding: 0.55rem 0.75rem;
  border: 1px solid var(--erp-line);
  border-radius: 8px;
  background: var(--erp-surface-muted);
  text-align: right;
}

.cash-rate-pill span {
  color: var(--erp-text-muted);
  font-size: 0.68rem;
  font-weight: 800;
  text-transform: uppercase;
}

.cash-rate-pill strong {
  color: var(--erp-text);
  font-size: 0.95rem;
}

.cash-denomination-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
  align-items: start;
}

.cash-denomination-card {
  display: grid;
  gap: 0.8rem;
  align-content: start;
  align-self: start;
  min-width: 0;
  padding: 1rem;
  border: 1px solid var(--erp-line);
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 10px 28px rgba(15, 23, 42, 0.06);
}

.cash-denomination-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding-bottom: 0.65rem;
  border-bottom: 1px solid var(--erp-line);
}

.cash-denomination-head span {
  display: block;
  color: var(--erp-text-muted);
  font-size: 0.72rem;
  font-weight: 800;
  text-transform: uppercase;
}

.cash-denomination-head h4 {
  margin: 0;
  color: var(--erp-text);
  font-size: 1.15rem;
}

.cash-denomination-head i {
  display: grid;
  place-items: center;
  width: 2.4rem;
  height: 2.4rem;
  border-radius: 8px;
  background: var(--erp-surface-muted);
  color: var(--erp-primary);
  font-size: 1.2rem;
}

.cash-denomination-table {
  display: grid;
  gap: 0.4rem;
}

.cash-denomination-row {
  display: grid;
  grid-template-columns: minmax(5rem, 0.9fr) minmax(5.5rem, 0.75fr) minmax(7.5rem, 1fr);
  align-items: center;
  min-height: 2.45rem;
  gap: 0.5rem;
  padding: 0.35rem 0.45rem;
  border-radius: 7px;
  background: #fff;
}

.cash-denomination-row-head {
  min-height: auto;
  padding-top: 0;
  padding-bottom: 0;
  background: transparent;
  color: var(--erp-text-muted);
  font-size: 0.7rem;
  font-weight: 800;
  text-transform: uppercase;
}

.cash-denomination-row .form-control {
  height: 2.15rem;
  min-width: 0;
  padding: 0.3rem 0.45rem;
  text-align: right;
}

.cash-denomination-row strong {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  text-align: right;
  white-space: nowrap;
}

.cash-movement-form {
  display: grid;
  grid-template-columns: 8rem minmax(0, 1fr) 9rem auto;
  gap: 0.5rem;
}

.cash-movement-list {
  display: grid;
  gap: 0.5rem;
}

.cash-movement-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto auto;
  align-items: center;
  gap: 0.5rem;
}

.cash-close-voucher-note {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.cash-close-voucher-note h3,
.cash-close-voucher-note p {
  margin: 0;
}

.cash-close-voucher-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  min-height: 2.5rem;
  padding: 0.55rem 0.9rem;
  border: 1px solid var(--erp-line);
  border-radius: 8px;
  background: var(--erp-primary);
  color: #fff;
  font-weight: 800;
  text-decoration: none;
  white-space: nowrap;
}

.positive {
  color: var(--erp-success);
}

.negative {
  color: var(--erp-danger);
}

.cash-receipt-print {
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
.cash-receipt-print h4,
.receipt-center p,
.receipt-note {
  margin: 0;
}

.cash-receipt-print h4 {
  font-size: 0.82rem;
  text-transform: uppercase;
}

.cash-receipt-print hr {
  margin: 0.55rem 0;
  border: 0;
  border-top: 1px dashed #222;
}

.receipt-lines,
.receipt-movements {
  display: grid;
  gap: 0.2rem;
}

.receipt-lines div,
.receipt-movement-row,
.receipt-result {
  display: flex;
  justify-content: space-between;
  gap: 0.65rem;
}

.receipt-lines span,
.receipt-movement-row span,
.receipt-result span {
  min-width: 0;
}

.receipt-lines strong,
.receipt-movement-row strong,
.receipt-result strong {
  text-align: right;
  white-space: nowrap;
}

.receipt-result {
  padding: 0.35rem 0;
  font-size: 0.95rem;
  text-transform: uppercase;
}

.receipt-result.sobrante {
  color: #075985;
}

.receipt-result.faltante {
  color: #b91c1c;
}

.receipt-result.cuadrado {
  color: #166534;
}

.receipt-signature {
  margin-top: 2rem;
  padding-top: 0.35rem;
  border-top: 1px solid #111;
  text-align: center;
}

@media print {
  :global(body.printing-cash-close *) {
    visibility: hidden !important;
  }

  :global(body.printing-cash-close .cash-receipt-print),
  :global(body.printing-cash-close .cash-receipt-print *) {
    visibility: visible !important;
  }

  :global(body.printing-cash-close .cash-receipt-print) {
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
  .cash-close-layout,
  .cash-close-kpis,
  .cash-close-totals,
  .cash-denomination-grid,
  .cash-movement-form {
    grid-template-columns: minmax(0, 1fr);
  }

  .cash-close-controls {
    display: flex;
  }

  .cash-close-voucher-note {
    align-items: stretch;
    flex-direction: column;
  }

  .cash-denomination-row {
    grid-template-columns: minmax(4.8rem, 0.8fr) minmax(5rem, 0.7fr) minmax(6.7rem, 1fr);
  }
}

@media (max-width: 560px) {
  .cash-denomination-card {
    padding: 0.75rem;
  }

  .cash-denomination-row {
    grid-template-columns: minmax(4.2rem, 0.7fr) minmax(4.8rem, 0.75fr) minmax(5.8rem, 0.9fr);
    gap: 0.35rem;
    padding-inline: 0;
  }

  .cash-denomination-row,
  .cash-denomination-row .form-control,
  .cash-denomination-row strong {
    font-size: 0.78rem;
  }

  .cash-denomination-row .form-control {
    height: 2rem;
  }

  .cash-close-compact-field {
    width: 100%;
    max-width: none;
  }
}
</style>
