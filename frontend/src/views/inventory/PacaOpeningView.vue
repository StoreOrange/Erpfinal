<!--
  Pantalla de apertura de pacas.
  Hecho por Carlos.
  Colaboracion academica: Oded Garcia y Carlos Ramirez.
  Nota: este modulo transforma una paca en productos clasificados.
-->
<template>
  <section class="page-section paca-page">
    <header class="module-hero">
      <div class="module-hero-copy">
        <p class="page-kicker">Inventario</p>
        <h1 class="page-title">Apertura de pacas</h1>
        <p class="panel-text">
          Da de baja una paca, ingresa la clasificacion resultante y genera un informe de costo,
          valor producido, ganancia o perdida.
        </p>
      </div>
      <div class="module-hero-meta">
        <div class="module-meta-box">
          <span>Aperturas</span>
          <strong>{{ openings.length }}</strong>
        </div>
        <div class="module-meta-box">
          <span>Ultimo informe</span>
          <strong>{{ selectedReport ? `PAC-${selectedReport.id}` : "Pendiente" }}</strong>
        </div>
        <div class="module-meta-box">
          <span>Resultado</span>
          <strong :class="resultClass(selectedReport?.diferencia_cs)">
            C$ {{ formatMoney(selectedReport?.diferencia_cs || 0) }}
          </strong>
        </div>
      </div>
    </header>

    <div class="paca-tabs">
      <button type="button" :class="{ active: activeTab === 'form' }" @click="activeTab = 'form'">
        <i class="bi bi-box-arrow-in-down"></i>
        Nueva apertura
      </button>
      <button type="button" :class="{ active: activeTab === 'history' }" @click="activeTab = 'history'">
        <i class="bi bi-clock-history"></i>
        Historico y reimpresion
        <span>{{ openings.length }}</span>
      </button>
    </div>

    <div class="paca-tab-panel">
      <section v-if="activeTab === 'form'" class="panel-card movement-entry-card">
        <div class="movement-card-head">
          <div>
            <span class="products-section-kicker">Operacion</span>
            <h3>Nueva apertura</h3>
            <p>Selecciona la paca origen y registra los productos clasificados que ingresan.</p>
          </div>
          <Tag severity="warn" value="Paca" rounded />
        </div>

        <form class="movement-form" @submit.prevent="submitOpening">
          <div class="movement-form-grid">
            <label class="field-group">
              <span>Bodega origen</span>
              <Select
                v-model="form.bodega_id"
                :options="catalogs.bodegas"
                option-label="name"
                option-value="id"
                placeholder="Bodega de salida"
                filter
                :filter-fields="['name', 'code']"
                @change="syncDefaultDestinationBodega"
              />
            </label>

            <label class="field-group">
              <span>Bodega destino</span>
              <Select
                v-model="form.bodega_destino_id"
                :options="catalogs.bodegas"
                option-label="name"
                option-value="id"
                placeholder="Bodega donde ingresa lo producido"
                filter
                :filter-fields="['name', 'code']"
              />
            </label>

            <div class="field-group movement-date-field">
              <span>Fecha</span>
              <div ref="pacaDatePickerRef" class="movement-date-control" :class="{ open: pacaDatePickerOpen }">
                <button type="button" class="movement-date-display" @click="togglePacaDatePicker">
                  <strong>{{ formattedPacaDate }}</strong>
                  <i class="bi bi-calendar3" aria-hidden="true"></i>
                </button>

                <div v-if="pacaDatePickerOpen" class="movement-date-picker" role="dialog" aria-label="Seleccionar fecha de apertura">
                  <div class="movement-date-picker-head">
                    <button type="button" aria-label="Mes anterior" @click="movePacaDateMonth(-1)">
                      <i class="bi bi-chevron-left"></i>
                    </button>
                    <strong>{{ pacaDateMonthLabel }}</strong>
                    <button type="button" aria-label="Mes siguiente" @click="movePacaDateMonth(1)">
                      <i class="bi bi-chevron-right"></i>
                    </button>
                  </div>
                  <div class="movement-date-weekdays">
                    <span v-for="day in pacaDateWeekdays" :key="day">{{ day }}</span>
                  </div>
                  <div class="movement-date-days">
                    <button
                      v-for="day in pacaDateCalendarDays"
                      :key="day.key"
                      type="button"
                      :class="{ muted: !day.currentMonth, today: day.isToday, selected: day.isSelected }"
                      @click="selectPacaDate(day.iso)"
                    >
                      {{ day.day }}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <label class="field-group">
              <span>Moneda valores</span>
              <select v-model="form.moneda" class="form-control">
                <option value="CS">Cordobas (C$)</option>
                <option value="USD">Dolares (USD)</option>
              </select>
            </label>

            <label class="field-group">
              <span>Tasa vigente</span>
              <InputNumber
                v-model="form.tasa_cambio"
                :min="0"
                :min-fraction-digits="2"
                :max-fraction-digits="4"
                disabled
              />
              <small class="field-help">Tomada de Datos > Tasa de cambio.</small>
            </label>

            <div class="field-group field-span-2 paca-source-picker">
              <span>Paca origen</span>
              <div class="paca-source-add">
                <Select
                  v-model="sourceDraft.producto_id"
                  :options="products"
                  option-label="descripcion"
                  option-value="id"
                  placeholder="Seleccionar producto paca"
                  filter
                  :filter-fields="['cod_producto', 'descripcion']"
                  @update:model-value="handleSourceProductChange(sourceDraft)"
                >
                  <template #value="{ value, placeholder }">
                    <span v-if="value" class="paca-selected-value">
                      {{ productCode(value) }} - {{ productLabel(value) }}
                    </span>
                    <span v-else>{{ placeholder }}</span>
                  </template>
                  <template #option="{ option }">
                    <div class="paca-product-option">
                      <div>
                        <strong>{{ option.descripcion }}</strong>
                        <small>{{ option.cod_producto }}</small>
                      </div>
                      <div>
                        <span>Seleccione para ver saldo en origen</span>
                        <span>Costo C$ {{ formatMoney(option.costo_producto) }}</span>
                      </div>
                    </div>
                  </template>
                </Select>
                <InputNumber
                  v-model="sourceDraft.cantidad"
                  :min="0.01"
                  :max="sourceAvailable(sourceDraft) || undefined"
                  :min-fraction-digits="2"
                  :max-fraction-digits="4"
                  placeholder="Cantidad"
                />
                <Button
                  type="button"
                  icon="bi bi-plus-lg"
                  label="Agregar paca"
                  severity="secondary"
                  variant="outlined"
                  :disabled="!canAddSourceDraft"
                  @click="addSourcePaca"
                />
              </div>
              <div v-if="sourceDraft.producto_id" class="paca-source-info">
                <div>
                  <span>Producto seleccionado</span>
                  <strong>{{ productCode(sourceDraft.producto_id) }} - {{ productLabel(sourceDraft.producto_id) }}</strong>
                </div>
                <div>
                  <span>Disponible en bodega origen</span>
                  <strong :class="{ 'paca-negative': sourceAvailable(sourceDraft) <= 0 }">
                    {{ formatQty(sourceAvailable(sourceDraft)) }}
                  </strong>
                </div>
                <div>
                  <span>Costo unitario</span>
                  <strong>{{ currencySymbol }} {{ formatMoney(sourceDraft.precio_unitario || 0) }}</strong>
                </div>
              </div>
              <small v-if="sourceDraft.producto_id && sourceAvailable(sourceDraft) <= 0" class="paca-stock-warning">
                La bodega origen seleccionada no tiene existencia disponible para esta paca.
              </small>
            </div>

            <label class="field-group field-span-2">
              <span>Observacion</span>
              <textarea v-model="form.observacion" class="form-control movement-notes" rows="2" placeholder="Referencia, lote o detalle de la apertura"></textarea>
            </label>
          </div>

          <div class="paca-lines-card">
            <div class="movement-card-head paca-lines-head">
              <div>
                <span class="products-section-kicker">Pacas origen</span>
                <h3>Pacas a abrir</h3>
              </div>
              <Tag severity="info" :value="`${sourceLines.length} origen(es)`" rounded />
            </div>

            <div class="paca-source-grid">
              <div v-for="(source, index) in sourceLines" :key="source.key" class="paca-source-row">
                <div class="products-main-cell">
                  <strong>{{ productLabel(source.producto_id) }}</strong>
                  <small>{{ productCode(source.producto_id) }}</small>
                </div>
                <label class="field-group">
                  <span>Cantidad</span>
                  <InputNumber
                    v-model="source.cantidad"
                    :min="0.01"
                    :max="sourceAvailable(source) || undefined"
                    :min-fraction-digits="2"
                    :max-fraction-digits="4"
                    @update:model-value="validateSourceLine(source)"
                  />
                </label>
                <div class="paca-line-total">
                  <span>Saldo origen</span>
                  <strong :class="{ 'paca-negative': Number(source.cantidad || 0) > sourceAvailable(source) }">
                    {{ formatQty(sourceAvailable(source)) }}
                  </strong>
                </div>
                <div class="paca-line-total">
                  <span>Costo unitario</span>
                  <strong>{{ currencySymbol }} {{ formatMoney(source.precio_unitario || 0) }}</strong>
                </div>
                <div class="paca-line-total">
                  <span>Total baja</span>
                  <strong>{{ currencySymbol }} {{ formatMoney(sourceTotal(source)) }}</strong>
                </div>
                <Button type="button" icon="bi bi-trash" severity="danger" variant="text" rounded @click="removeSourcePaca(index)" />
              </div>
            </div>
          </div>

          <div class="paca-lines-card">
            <div class="movement-card-head paca-lines-head">
              <div>
                <span class="products-section-kicker">Clasificacion</span>
                <h3>Productos resultantes</h3>
              </div>
              <Button type="button" icon="bi bi-plus-lg" label="Agregar linea" severity="secondary" variant="outlined" @click="addLine" />
            </div>

            <div class="paca-lines">
              <div v-for="(line, index) in lines" :key="line.key" class="paca-line">
                <label class="field-group paca-product-field">
                  <span>Producto</span>
                  <Select
                    v-model="line.producto_id"
                    :options="products"
                    option-label="descripcion"
                    option-value="id"
                    placeholder="Producto clasificado"
                    filter
                    :filter-fields="['cod_producto', 'descripcion']"
                    @change="applyProductEstimate(line)"
                  />
                </label>
                <label class="field-group">
                  <span>Cantidad</span>
                  <InputNumber v-model="line.cantidad" :min="0.01" :min-fraction-digits="2" :max-fraction-digits="4" />
                </label>
                <label class="field-group">
                  <span>Costo operativo</span>
                  <InputNumber
                    v-model="line.precio_estimado_unitario"
                    :min="0"
                    :min-fraction-digits="2"
                    :max-fraction-digits="2"
                    disabled
                  />
                </label>
                <div class="paca-line-total">
                  <span>Total producido</span>
                  <strong>{{ currencySymbol }} {{ formatMoney(lineTotal(line)) }}</strong>
                </div>
                <Button type="button" icon="bi bi-trash" severity="danger" variant="text" rounded @click="removeLine(index)" />
              </div>
            </div>
          </div>

          <div class="paca-summary">
            <div><span>Pacas abiertas</span><strong>{{ formatQty(totalSourceUnits) }}</strong></div>
            <div><span>Valor producido</span><strong>{{ currencySymbol }} {{ formatMoney(totalEstimated) }}</strong></div>
            <div><span>Resultado</span><strong :class="resultClass(totalEstimated - totalSourceCost)">{{ currencySymbol }} {{ formatMoney(totalEstimated - totalSourceCost) }}</strong></div>
          </div>

          <p v-if="formError" class="auth-error">{{ formError }}</p>
          <div class="movement-form-actions">
            <Button type="button" severity="secondary" variant="outlined" label="Limpiar" @click="resetForm" />
            <Button :loading="submitting" type="submit" icon="bi bi-box-arrow-in-down" label="Procesar apertura" />
          </div>
        </form>
      </section>

      <section v-else class="panel-card movement-history-card paca-history-panel">
        <div class="movement-card-head">
          <div>
            <span class="products-section-kicker">Informes</span>
            <h3>Historico de aperturas</h3>
            <p>Consulta documentos de baja, ingreso, resultado de costo y reimprime el informe PDF.</p>
          </div>
          <Button
            type="button"
            severity="secondary"
            variant="outlined"
            icon="bi bi-plus-lg"
            label="Nueva apertura"
            @click="activeTab = 'form'"
          />
        </div>

        <DataTable :value="openings" class="movements-table movement-history-table" paginator :rows="8" responsive-layout="scroll" size="small">
          <Column field="id" header="Doc." sortable>
            <template #body="{ data }">PAC-{{ data.id }}</template>
          </Column>
          <Column field="fecha" header="Fecha" sortable />
          <Column field="paca_producto.descripcion" header="Paca">
            <template #body="{ data }">
              <div class="products-main-cell">
                <strong>{{ data.paca_producto?.descripcion || "-" }}</strong>
                <small>{{ data.paca_producto?.cod_producto || "" }}</small>
              </div>
            </template>
          </Column>
          <Column field="valor_estimado_cs" header="Producido C$" sortable>
            <template #body="{ data }">C$ {{ formatMoney(data.valor_estimado_cs) }}</template>
          </Column>
          <Column field="diferencia_cs" header="Resultado" sortable>
            <template #body="{ data }">
              <Tag :severity="Number(data.diferencia_cs || 0) >= 0 ? 'success' : 'danger'" :value="`C$ ${formatMoney(data.diferencia_cs)}`" rounded />
            </template>
          </Column>
          <Column header="Acciones">
            <template #body="{ data }">
              <Button type="button" icon="bi bi-eye" severity="secondary" variant="text" rounded @click="viewReport(data.id)" />
            </template>
          </Column>
          <template #empty>
            <div class="empty-state">No hay aperturas registradas.</div>
          </template>
        </DataTable>

        <article v-if="selectedReport" class="paca-report">
          <div class="paca-report-head">
            <div>
              <span>Informe de apertura</span>
              <h3>PAC-{{ selectedReport.id }}</h3>
              <p>{{ selectedReport.paca_producto?.cod_producto }} / {{ selectedReport.paca_producto?.descripcion }}</p>
            </div>
            <Button type="button" icon="bi bi-printer" label="Imprimir / Guardar PDF" @click="printReport" />
          </div>

          <section class="paca-report-result" :class="resultClass(selectedReport.diferencia_cs)">
            <div>
              <span>Resultado financiero de la apertura</span>
              <strong>{{ reportResultLabel(selectedReport) }}</strong>
              <small>
                Diferencia entre el costo de la mercaderia abierta y el valor de la mercaderia resultante.
              </small>
            </div>
            <strong>C$ {{ formatMoney(selectedReport.diferencia_cs) }}</strong>
          </section>

          <div class="paca-report-kpis">
            <div><span>Costo origen</span><strong>C$ {{ formatMoney(selectedReport.costo_origen_cs) }}</strong></div>
            <div><span>Valor producido</span><strong>C$ {{ formatMoney(selectedReport.valor_estimado_cs) }}</strong></div>
            <div><span>Resultado</span><strong :class="resultClass(selectedReport.diferencia_cs)">C$ {{ formatMoney(selectedReport.diferencia_cs) }}</strong></div>
            <div><span>Variacion</span><strong :class="resultClass(selectedReport.diferencia_cs)">{{ formatPercent(reportDifferencePercent(selectedReport)) }}</strong></div>
            <div><span>Costo por paca</span><strong>C$ {{ formatMoney(reportCostPerSourceUnit(selectedReport)) }}</strong></div>
            <div><span>Valor por unidad resultante</span><strong>C$ {{ formatMoney(reportProducedValuePerUnit(selectedReport)) }}</strong></div>
          </div>

          <div class="paca-report-meta">
            <div><span>Fecha</span><strong>{{ selectedReport.fecha }}</strong></div>
            <div><span>Origen</span><strong>{{ selectedReport.bodega?.name || "-" }}</strong></div>
            <div><span>Destino</span><strong>{{ selectedReport.bodega_destino?.name || selectedReport.bodega?.name || "-" }}</strong></div>
            <div><span>Pacas</span><strong>{{ formatQty(selectedReport.cantidad_pacas) }}</strong></div>
            <div><span>Egreso</span><strong>EGR-{{ selectedReport.egreso_id }}</strong></div>
            <div><span>Ingreso</span><strong>ING-{{ selectedReport.ingreso_id }}</strong></div>
            <div><span>Usuario</span><strong>{{ selectedReport.usuario_registro || "-" }}</strong></div>
            <div><span>Tasa cambio</span><strong>C$ {{ formatMoney(selectedReport.tasa_cambio) }}</strong></div>
            <div><span>Estado</span><strong>{{ selectedReport.estado || "-" }}</strong></div>
          </div>

          <div v-if="selectedReport.observacion" class="paca-report-note">
            <span>Observacion</span>
            <p>{{ selectedReport.observacion }}</p>
          </div>

          <div class="paca-report-section-title">
            <strong>Mercaderia abierta</strong>
            <span>Costo descargado del inventario origen</span>
          </div>
          <DataTable :value="selectedReport.origenes || []" class="movements-table" responsive-layout="scroll" size="small">
            <Column field="producto.descripcion" header="Pacas origen">
              <template #body="{ data }">
                <div class="products-main-cell">
                  <strong>{{ data.producto?.descripcion || "-" }}</strong>
                  <small>{{ data.producto?.cod_producto || "" }}</small>
                </div>
              </template>
            </Column>
            <Column field="cantidad" header="Cantidad">
              <template #body="{ data }">{{ formatQty(data.cantidad) }}</template>
            </Column>
            <Column field="costo_unitario_cs" header="Costo unit. C$">
              <template #body="{ data }">C$ {{ formatMoney(data.costo_unitario_cs) }}</template>
            </Column>
            <Column field="subtotal_cs" header="Costo baja C$">
              <template #body="{ data }">C$ {{ formatMoney(data.subtotal_cs) }}</template>
            </Column>
          </DataTable>

          <div class="paca-report-section-title">
            <strong>Mercaderia resultante</strong>
            <span>Valor generado y costo asignado proporcionalmente</span>
          </div>
          <DataTable :value="selectedReport.lineas || []" class="movements-table" responsive-layout="scroll" size="small">
            <Column field="producto.descripcion" header="Producto">
              <template #body="{ data }">
                <div class="products-main-cell">
                  <strong>{{ data.producto?.descripcion || "-" }}</strong>
                  <small>{{ data.producto?.cod_producto || "" }}</small>
                </div>
              </template>
            </Column>
            <Column field="cantidad" header="Cantidad">
              <template #body="{ data }">{{ formatQty(data.cantidad) }}</template>
            </Column>
            <Column field="precio_estimado_unitario_cs" header="Valor unit. C$">
              <template #body="{ data }">C$ {{ formatMoney(data.precio_estimado_unitario_cs) }}</template>
            </Column>
            <Column field="valor_estimado_cs" header="Valor producido C$">
              <template #body="{ data }">C$ {{ formatMoney(data.valor_estimado_cs) }}</template>
            </Column>
            <Column field="costo_asignado_cs" header="Costo asignado">
              <template #body="{ data }">C$ {{ formatMoney(data.costo_asignado_cs) }}</template>
            </Column>
            <Column header="Diferencia">
              <template #body="{ data }">
                <strong :class="resultClass(lineDifferenceCs(data))">C$ {{ formatMoney(lineDifferenceCs(data)) }}</strong>
              </template>
            </Column>
          </DataTable>
        </article>
      </section>
    </div>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from "vue";
import Button from "primevue/button";
import Column from "primevue/column";
import DataTable from "primevue/datatable";
import InputNumber from "primevue/inputnumber";
import Select from "primevue/select";
import Tag from "primevue/tag";

import { readStoredUser } from "../../services/auth";
import {
  createPacaOpening,
  fetchInventoryCatalogs,
  fetchPacaOpeningReport,
  fetchPacaOpenings,
  fetchProductBalances,
  fetchProducts,
} from "../../services/inventory";
import { fetchCurrentExchangeRate } from "../../services/settings";

const currentUser = readStoredUser();
const products = ref([]);
const openings = ref([]);
const selectedReport = ref(null);
const submitting = ref(false);
const formError = ref("");
const activeTab = ref("form");
const pacaDatePickerRef = ref(null);
const pacaDatePickerOpen = ref(false);
const pacaDateViewDate = ref(new Date());
const catalogs = reactive({ bodegas: [] });
const form = reactive(getEmptyForm());
const sourceDraft = reactive(getEmptySource());
const sourceLines = ref([]);
const lines = ref([getEmptyLine()]);

const currencySymbol = computed(() => (form.moneda === "USD" ? "US$" : "C$"));
const totalSourceUnits = computed(() => sourceLines.value.reduce((sum, line) => sum + Number(line.cantidad || 0), 0));
const totalSourceCost = computed(() => sourceLines.value.reduce((sum, line) => sum + sourceTotal(line), 0));
const totalUnits = computed(() => lines.value.reduce((sum, line) => sum + Number(line.cantidad || 0), 0));
const totalEstimated = computed(() => lines.value.reduce((sum, line) => sum + lineTotal(line), 0));
const formattedPacaDate = computed(() => formatDisplayDate(form.fecha));
const canAddSourceDraft = computed(() => {
  if (!sourceDraft.producto_id) return false;
  const quantity = Number(sourceDraft.cantidad || 0);
  const available = sourceAvailable(sourceDraft);
  return quantity > 0 && available > 0 && quantity <= available;
});
const pacaDateWeekdays = ["Do", "Lu", "Ma", "Mi", "Ju", "Vi", "Sa"];
const pacaDateMonthLabel = computed(() =>
  new Intl.DateTimeFormat("es-NI", {
    month: "long",
    year: "numeric",
  }).format(pacaDateViewDate.value),
);
const pacaDateCalendarDays = computed(() => buildPacaDateCalendar(pacaDateViewDate.value, form.fecha));

function todayIsoDate() {
  return toIsoDate(new Date());
}

function getEmptyForm() {
  return {
    paca_producto_id: null,
    bodega_id: null,
    bodega_destino_id: null,
    fecha: todayIsoDate(),
    cantidad_pacas: 1,
    moneda: "CS",
    tasa_cambio: null,
    observacion: "",
    usuario_registro: currentUser?.email || "sistema",
  };
}

function getEmptySource() {
  return {
    key: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
    producto_id: null,
    cantidad: 1,
    precio_unitario: 0,
    existencia: null,
  };
}

function getEmptyLine() {
  return {
    key: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
    producto_id: null,
    cantidad: 1,
    precio_estimado_unitario: 0,
  };
}

function formatMoney(value) {
  return new Intl.NumberFormat("es-NI", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(Number(value || 0));
}

function formatQty(value) {
  return Number(value || 0).toFixed(2);
}

function formatPercent(value) {
  return `${new Intl.NumberFormat("es-NI", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(Number(value || 0))}%`;
}

function resultClass(value) {
  return Number(value || 0) >= 0 ? "paca-positive" : "paca-negative";
}

function reportResultLabel(report) {
  const difference = Number(report?.diferencia_cs || 0);
  if (difference > 0) return "Ganancia de inventario";
  if (difference < 0) return "Perdida de inventario";
  return "Sin diferencia";
}

function reportDifferencePercent(report) {
  const sourceCost = Number(report?.costo_origen_cs || 0);
  if (!sourceCost) return 0;
  return (Number(report?.diferencia_cs || 0) / sourceCost) * 100;
}

function reportCostPerSourceUnit(report) {
  const sourceUnits = Number(report?.cantidad_pacas || 0);
  if (!sourceUnits) return 0;
  return Number(report?.costo_origen_cs || 0) / sourceUnits;
}

function reportProducedValuePerUnit(report) {
  const producedUnits = (report?.lineas || []).reduce((sum, line) => sum + Number(line.cantidad || 0), 0);
  if (!producedUnits) return 0;
  return Number(report?.valor_estimado_cs || 0) / producedUnits;
}

function lineDifferenceCs(line) {
  return Number(line?.valor_estimado_cs || 0) - Number(line?.costo_asignado_cs || 0);
}

function lineTotal(line) {
  return Number(line.cantidad || 0) * Number(line.precio_estimado_unitario || 0);
}

function sourceTotal(line) {
  return Number(line.cantidad || 0) * Number(line.precio_unitario || 0);
}

function productById(productId) {
  return products.value.find((item) => item.id === productId) || null;
}

function productLabel(productId) {
  return productById(productId)?.descripcion || "-";
}

function productCode(productId) {
  return productById(productId)?.cod_producto || "";
}

function sourceAvailable(source) {
  if (source?.existencia !== null && source?.existencia !== undefined) {
    return Number(source.existencia || 0);
  }
  return 0;
}

function toIsoDate(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function formatDisplayDate(value) {
  const [year, month, day] = String(value || todayIsoDate()).split("-").map(Number);
  if (!year || !month || !day) return value || "-";
  return `${String(day).padStart(2, "0")}-${String(month).padStart(2, "0")}-${year}`;
}

function parseIsoDate(value) {
  const [year, month, day] = String(value || todayIsoDate()).split("-").map(Number);
  return new Date(year, month - 1, day || 1);
}

function buildPacaDateCalendar(viewDate, selectedIso) {
  const year = viewDate.getFullYear();
  const month = viewDate.getMonth();
  const firstDay = new Date(year, month, 1);
  const start = new Date(year, month, 1 - firstDay.getDay());
  const today = todayIsoDate();
  return Array.from({ length: 42 }, (_, index) => {
    const date = new Date(start);
    date.setDate(start.getDate() + index);
    const iso = toIsoDate(date);
    return {
      key: `${iso}-${index}`,
      iso,
      day: date.getDate(),
      currentMonth: date.getMonth() === month,
      isToday: iso === today,
      isSelected: iso === selectedIso,
    };
  });
}

function togglePacaDatePicker() {
  pacaDateViewDate.value = parseIsoDate(form.fecha);
  pacaDatePickerOpen.value = !pacaDatePickerOpen.value;
}

function movePacaDateMonth(direction) {
  const nextDate = new Date(pacaDateViewDate.value);
  nextDate.setMonth(nextDate.getMonth() + direction);
  pacaDateViewDate.value = nextDate;
}

function selectPacaDate(isoDate) {
  form.fecha = isoDate;
  pacaDateViewDate.value = parseIsoDate(isoDate);
  pacaDatePickerOpen.value = false;
}

function handlePacaDateOutsideClick(event) {
  if (!pacaDatePickerOpen.value) return;
  const root = pacaDatePickerRef.value;
  if (root && !root.contains(event.target)) {
    pacaDatePickerOpen.value = false;
  }
}

function applySourceEstimate(source) {
  const product = productById(source.producto_id);
  if (!product) {
    source.precio_unitario = 0;
    source.existencia = 0;
    return;
  }
  const storedCost = Number(product.costo_producto || 0);
  if (form.moneda === "USD" && Number(form.tasa_cambio || 0) > 0) {
    source.precio_unitario = Number((storedCost / Number(form.tasa_cambio)).toFixed(2));
    return;
  }
  source.precio_unitario = storedCost;
}

function validateSourceLine(source) {
  applySourceEstimate(source);
  if (!source?.producto_id) return;
  const available = sourceAvailable(source);
  if (Number(source.cantidad || 0) > available) {
    formError.value = `Existencia insuficiente para ${productLabel(source.producto_id)}. Disponible: ${formatQty(available)}.`;
    source.cantidad = available > 0 ? available : 0.01;
    return;
  }
  if (formError.value?.startsWith("Existencia insuficiente")) {
    formError.value = "";
  }
}

async function refreshSourceBalance(source) {
  if (!source?.producto_id || !form.bodega_id) {
    source.existencia = null;
    return;
  }
  source.existencia = null;
  try {
    const balances = await fetchProductBalances(source.producto_id);
    const row = balances.find((item) => Number(item.bodega_id) === Number(form.bodega_id));
    source.existencia = Number(row?.existencia || 0);
  } catch {
    source.existencia = 0;
    formError.value = "No se pudo consultar la existencia por bodega. Intenta nuevamente antes de procesar.";
  }
}

async function handleSourceProductChange(source) {
  applySourceEstimate(source);
  await refreshSourceBalance(source);
  validateSourceLine(source);
}

function resetSourceDraft() {
  Object.assign(sourceDraft, getEmptySource());
}

function addSourcePaca() {
  formError.value = "";
  if (!sourceDraft.producto_id) {
    formError.value = "Selecciona una paca origen.";
    return;
  }
  if (Number(sourceDraft.cantidad || 0) <= 0) {
    formError.value = "La cantidad de la paca origen debe ser mayor que cero.";
    return;
  }
  if (Number(sourceDraft.cantidad || 0) > sourceAvailable(sourceDraft)) {
    formError.value = `Existencia insuficiente para la paca seleccionada. Disponible: ${formatQty(sourceAvailable(sourceDraft))}.`;
    return;
  }
  const existing = sourceLines.value.find((item) => item.producto_id === sourceDraft.producto_id);
  if (existing) {
    const nextQuantity = Number(existing.cantidad || 0) + Number(sourceDraft.cantidad || 0);
    if (nextQuantity > sourceAvailable(existing)) {
      formError.value = `Existencia insuficiente para ${productLabel(existing.producto_id)}. Disponible: ${formatQty(sourceAvailable(existing))}.`;
      return;
    }
    existing.cantidad = nextQuantity;
    applySourceEstimate(existing);
  } else {
    const nextSource = {
      ...getEmptySource(),
      producto_id: sourceDraft.producto_id,
      cantidad: Number(sourceDraft.cantidad || 0),
      precio_unitario: Number(sourceDraft.precio_unitario || 0),
      existencia: Number(sourceAvailable(sourceDraft) || 0),
    };
    applySourceEstimate(nextSource);
    sourceLines.value.push(nextSource);
  }
  resetSourceDraft();
}

function removeSourcePaca(index) {
  sourceLines.value.splice(index, 1);
}

function addLine() {
  lines.value.push(getEmptyLine());
}

function removeLine(index) {
  if (lines.value.length === 1) return;
  lines.value.splice(index, 1);
}

function applyProductEstimate(line) {
  const product = products.value.find((item) => item.id === line.producto_id);
  if (!product) return;
  const storedCost = Number(product.costo_producto || 0);
  if (form.moneda === "USD" && Number(form.tasa_cambio || 0) > 0) {
    line.precio_estimado_unitario = Number((storedCost / Number(form.tasa_cambio)).toFixed(2));
    return;
  }
  line.precio_estimado_unitario = storedCost;
}

function resetForm() {
  Object.assign(form, getEmptyForm());
  setDefaultBodegas();
  sourceLines.value = [];
  resetSourceDraft();
  lines.value = [getEmptyLine()];
  formError.value = "";
  void applyCurrentExchangeRate();
}

async function applyCurrentExchangeRate() {
  try {
    const currentRate = await fetchCurrentExchangeRate();
    form.tasa_cambio = currentRate?.rate ? Number(currentRate.rate) : null;
  } catch {
    form.tasa_cambio = null;
  }
}

function setDefaultBodegas() {
  if (!catalogs.bodegas.length) return;
  if (!form.bodega_id) form.bodega_id = catalogs.bodegas[0].id;
  if (!form.bodega_destino_id) form.bodega_destino_id = form.bodega_id;
}

function syncDefaultDestinationBodega() {
  if (!form.bodega_destino_id) {
    form.bodega_destino_id = form.bodega_id;
  }
}

watch(
  () => form.bodega_id,
  async (nextBodegaId, previousBodegaId) => {
    if (!nextBodegaId) return;
    if (!form.bodega_destino_id || form.bodega_destino_id === previousBodegaId) {
      form.bodega_destino_id = nextBodegaId;
    }
    await Promise.all(sourceLines.value.map((source) => refreshSourceBalance(source)));
    sourceLines.value.forEach((source) => validateSourceLine(source));
    if (sourceDraft.producto_id) {
      await refreshSourceBalance(sourceDraft);
      validateSourceLine(sourceDraft);
    }
  },
);

watch(
  () => [form.moneda, form.tasa_cambio],
  () => {
    sourceLines.value.forEach((source) => applySourceEstimate(source));
    lines.value.forEach((line) => applyProductEstimate(line));
    if (sourceDraft.producto_id) applySourceEstimate(sourceDraft);
  },
);

watch(
  () => sourceDraft.producto_id,
  async (productId) => {
    if (!productId) return;
    await handleSourceProductChange(sourceDraft);
  },
);

async function loadData() {
  const [catalogData, productData, openingsData] = await Promise.all([
    fetchInventoryCatalogs(),
    fetchProducts("", true),
    fetchPacaOpenings(),
  ]);
  catalogs.bodegas = catalogData.bodegas || [];
  products.value = productData || [];
  openings.value = openingsData || [];
  setDefaultBodegas();
}

function validateForm() {
  if (!form.bodega_id) return "Selecciona la bodega origen.";
  if (!form.bodega_destino_id) return "Selecciona la bodega destino.";
  if (!sourceLines.value.length) return "Agrega al menos una paca origen.";
  if (sourceLines.value.some((line) => !line.producto_id || Number(line.cantidad || 0) <= 0)) {
    return "Cada paca origen debe tener producto y cantidad valida.";
  }
  const overStockSource = sourceLines.value.find((line) => Number(line.cantidad || 0) > sourceAvailable(line));
  if (overStockSource) {
    return `Existencia insuficiente para ${productLabel(overStockSource.producto_id)}. Disponible: ${formatQty(sourceAvailable(overStockSource))}.`;
  }
  if (Number(form.tasa_cambio || 0) <= 0) return "Registra una tasa de cambio vigente en Datos antes de procesar.";
  if (!lines.value.length) return "Agrega al menos un producto clasificado.";
  const invalidLine = lines.value.find((line) => !line.producto_id || Number(line.cantidad || 0) <= 0);
  if (invalidLine) return "Cada linea debe tener producto y cantidad valida.";
  return "";
}

async function submitOpening() {
  formError.value = validateForm();
  if (formError.value) return;
  submitting.value = true;
  try {
    const payload = {
      ...form,
      paca_producto_id: sourceLines.value[0].producto_id,
      cantidad_pacas: Number(totalSourceUnits.value || 0),
      bodega_destino_id: form.bodega_destino_id || form.bodega_id,
      tasa_cambio: Number(form.tasa_cambio || 0) > 0 ? Number(form.tasa_cambio || 0) : null,
      pacas_origen: sourceLines.value.map((line) => ({
        producto_id: line.producto_id,
        cantidad: Number(line.cantidad || 0),
      })),
      lineas: lines.value.map((line) => ({
        producto_id: line.producto_id,
        cantidad: Number(line.cantidad || 0),
        precio_estimado_unitario: 0,
      })),
    };
    const report = await createPacaOpening(payload);
    await loadData();
    selectedReport.value = await fetchPacaOpeningReport(report.id);
    activeTab.value = "history";
    resetForm();
    window.setTimeout(printReport, 350);
  } catch (error) {
    formError.value = error.message || "No se pudo procesar la apertura de paca.";
  } finally {
    submitting.value = false;
  }
}

async function viewReport(openingId) {
  selectedReport.value = await fetchPacaOpeningReport(openingId);
}

function printReport() {
  document.body.classList.add("printing-paca-report");
  window.print();
  window.setTimeout(() => document.body.classList.remove("printing-paca-report"), 500);
}

onMounted(async () => {
  document.addEventListener("click", handlePacaDateOutsideClick);
  try {
    await loadData();
    await applyCurrentExchangeRate();
  } catch (error) {
    formError.value = error.message || "No se pudo cargar apertura de pacas.";
  }
});

onBeforeUnmount(() => {
  document.removeEventListener("click", handlePacaDateOutsideClick);
});
</script>
