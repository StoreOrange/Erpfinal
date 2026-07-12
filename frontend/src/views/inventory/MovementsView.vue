<!--
  Pantalla de ingresos y egresos de inventario.
  Hecho por Carlos.
  Colaboracion academica: Oded Garcia y Carlos Ramirez.
  Recordatorio: revisar bien cantidades y bodegas antes de guardar movimientos.
-->
<template>
  <section class="page-section movements-page">
    <header class="module-hero movements-compact-hero">
      <div class="module-hero-copy">
        <p class="page-kicker">Inventario</p>
        <h1 class="page-title">Ingresos y egresos</h1>
        <p class="panel-text">
          Control operativo por bodega con trazabilidad documental.
        </p>
      </div>
      <div class="module-hero-meta movements-compact-stats">
        <div class="module-meta-box movements-compact-stat">
          <span>Ingresos</span>
          <strong>{{ ingresos.length }}</strong>
        </div>
        <div class="module-meta-box movements-compact-stat">
          <span>Egresos</span>
          <strong>{{ egresos.length }}</strong>
        </div>
        <div class="module-meta-box movements-compact-stat movements-compact-total">
          <span>Total del dia</span>
          <strong>{{ baseCurrencySymbol }} {{ formatMoney(movementTotalCs) }}</strong>
        </div>
      </div>
    </header>

    <div class="movements-modebar">
      <button type="button" class="movements-modechip" :class="{ active: activeSection === 'ingreso' }" @click="switchMode('ingreso')">
        <i class="bi bi-box-arrow-in-down"></i>
        <span>Ingreso</span>
      </button>
      <button type="button" class="movements-modechip" :class="{ active: activeSection === 'egreso' }" @click="switchMode('egreso')">
        <i class="bi bi-box-arrow-up-right"></i>
        <span>Egreso</span>
      </button>
      <button type="button" class="movements-modechip" :class="{ active: activeSection === 'historico' }" @click="activeSection = 'historico'">
        <i class="bi bi-clock-history"></i>
        <span>Historico</span>
      </button>
      <Tag severity="info" :value="`Bodegas: ${catalogs.bodegas.length}`" rounded />
      <Tag severity="contrast" :value="`Proveedores: ${catalogs.proveedores.length}`" rounded />
    </div>

    <div v-if="activeSection !== 'historico'" class="movements-layout movements-entry-layout">
      <section class="panel-card movement-entry-card">
        <div class="movement-card-head">
          <div>
            <span class="products-section-kicker">Registro operativo</span>
            <h3>{{ mode === "ingreso" ? "Nuevo ingreso" : "Nuevo egreso" }}</h3>
            <p>{{ modeCopy }}</p>
          </div>
          <Tag :severity="mode === 'ingreso' ? 'success' : 'warn'" :value="mode === 'ingreso' ? 'Entrada' : 'Salida'" />
        </div>

        <form class="movement-form" @submit.prevent="submitMovement">
          <div class="movement-form-grid">
            <label class="field-group">
              <span>{{ mode === "ingreso" ? "Tipo de ingreso" : "Tipo de egreso" }}</span>
              <Select
                v-model="form.tipo_id"
                :options="movementTypeOptions"
                option-label="nombre"
                option-value="id"
                placeholder="Seleccionar"
                filter
                :filter-fields="['nombre']"
              />
            </label>

            <label class="field-group">
              <span>Bodega</span>
              <Select
                v-model="form.bodega_id"
                :options="catalogs.bodegas"
                option-label="name"
                option-value="id"
                placeholder="Seleccionar"
                filter
                :filter-fields="['name', 'code']"
              />
            </label>

            <div class="field-group movement-date-field">
              <span>Fecha</span>
              <div ref="movementDatePickerRef" class="movement-date-control" :class="{ open: movementDatePickerOpen }">
                <button type="button" class="movement-date-display" @click="toggleMovementDatePicker">
                  <strong>{{ formattedMovementDate }}</strong>
                  <i class="bi bi-calendar3" aria-hidden="true"></i>
                </button>

                <div v-if="movementDatePickerOpen" class="movement-date-picker" role="dialog" aria-label="Seleccionar fecha">
                  <div class="movement-date-picker-head">
                    <button type="button" aria-label="Mes anterior" @click="moveMovementDateMonth(-1)">
                      <i class="bi bi-chevron-left"></i>
                    </button>
                    <strong>{{ movementDateMonthLabel }}</strong>
                    <button type="button" aria-label="Mes siguiente" @click="moveMovementDateMonth(1)">
                      <i class="bi bi-chevron-right"></i>
                    </button>
                  </div>
                  <div class="movement-date-weekdays">
                    <span v-for="day in movementDateWeekdays" :key="day">{{ day }}</span>
                  </div>
                  <div class="movement-date-days">
                    <button
                      v-for="day in movementDateCalendarDays"
                      :key="day.key"
                      type="button"
                      :class="{ muted: !day.currentMonth, today: day.isToday, selected: day.isSelected }"
                      @click="selectMovementDate(day.iso)"
                    >
                      {{ day.day }}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <label class="field-group">
              <span>Moneda</span>
              <select v-model="form.moneda" class="form-control">
                <option value="CS">Cordobas (C$)</option>
                <option value="USD">Dolares (USD)</option>
              </select>
            </label>

            <label class="field-group">
              <span>Tasa de cambio</span>
              <div class="movement-readonly-rate">
                <strong>C$ {{ formatMoney(exchangeRate) }}</strong>
                <small>Tasa vigente configurada</small>
              </div>
              <small class="movement-money-hint">1 USD = C$ {{ formatMoney(exchangeRate) }}</small>
            </label>

            <label v-if="mode === 'ingreso'" class="field-group field-span-2">
              <span>Proveedor</span>
              <div class="movement-provider-stack">
                <div class="movement-provider-row">
                  <Select
                    v-model="form.proveedor_id"
                    :options="catalogs.proveedores"
                    option-label="nombre"
                    option-value="id"
                    placeholder="Seleccionar"
                    filter
                    :filter-fields="['nombre', 'tipo']"
                    show-clear
                  />
                  <Button
                    type="button"
                    severity="secondary"
                    variant="outlined"
                    icon="bi bi-plus-lg"
                    label="Proveedor"
                    @click="showQuickProvider = !showQuickProvider"
                  />
                </div>
                <div v-if="showQuickProvider" class="movement-provider-quick">
                  <div class="movement-provider-quick-grid">
                    <label class="field-group">
                      <span>Nombre</span>
                      <input v-model="quickProvider.nombre" class="form-control" placeholder="Nombre del proveedor" />
                    </label>
                    <label class="field-group">
                      <span>Tipo</span>
                      <input v-model="quickProvider.tipo" class="form-control" placeholder="Local / Importacion" />
                    </label>
                  </div>
                  <div class="movement-provider-actions">
                    <label class="products-checkbox products-checkbox-compact">
                      <input v-model="quickProvider.activo" type="checkbox" />
                      <span>Activo</span>
                    </label>
                    <Button
                      type="button"
                      :loading="savingQuickProvider"
                      icon="bi bi-save2"
                      label="Guardar proveedor"
                      @click="submitQuickProvider"
                    />
                  </div>
                </div>
              </div>
            </label>

            <label v-if="showDestinationBodega" class="field-group field-span-2">
              <span>Bodega destino</span>
              <Select
                v-model="form.bodega_destino_id"
                :options="destinationBodegas"
                option-label="name"
                option-value="id"
                placeholder="Seleccionar"
                filter
                :filter-fields="['name', 'code']"
              />
            </label>

            <label class="field-group field-span-2">
              <span>Observacion</span>
              <textarea
                v-model="form.observacion"
                class="form-control movement-notes"
                rows="2"
                placeholder="Detalle operativo del movimiento"
              ></textarea>
            </label>
          </div>

          <div class="movement-product-head">
            <div>
              <span class="products-section-kicker">Detalle</span>
              <h4>Productos del movimiento</h4>
            </div>
          </div>

          <div class="movement-product-search">
            <div class="movement-search-box">
              <i class="bi bi-search" aria-hidden="true"></i>
              <InputText
                v-model="searchQuery"
                class="search-input movement-search-input"
                type="search"
                placeholder="Buscar por codigo, barra o descripcion"
                @keydown.down.prevent="moveSearchSelection(1)"
                @keydown.up.prevent="moveSearchSelection(-1)"
                @keydown.enter.prevent="handleSearchEnter"
              />
            </div>

            <div class="movement-search-results" v-if="searchQuery.trim().length >= 2">
              <div v-if="searchingProducts" class="empty-state">Buscando productos...</div>
              <div v-else-if="searchResults.length === 0" class="empty-state">Sin resultados para esta busqueda.</div>
              <button
                v-for="(item, index) in searchResults"
                :key="item.id"
                type="button"
                class="movement-result-item"
                :class="{ active: searchActiveIndex === index }"
                :ref="(el) => setSearchResultButton(el, index)"
                @click="selectProduct(item)"
              >
                <div>
                  <strong>{{ item.descripcion }}</strong>
                  <span>{{ item.cod_producto }}<template v-if="item.codigo_barra"> / {{ item.codigo_barra }}</template></span>
                </div>
                <Tag severity="contrast" :value="`Stock: ${formatQty(item.existencia)}`" rounded />
              </button>
            </div>
          </div>

          <div v-if="draft.product_id" class="movement-draft-row movement-draft-entry">
            <div class="movement-draft-main movement-draft-product">
              <span class="movement-draft-eyebrow">Producto seleccionado</span>
              <strong>{{ draft.descripcion }}</strong>
              <div class="movement-draft-tags">
                <span>{{ draft.cod_producto }}</span>
                <span>Disponible {{ formatQty(draft.existencia) }}</span>
                <span v-if="draftEquivalentText">Ref. {{ draftEquivalentText }}</span>
              </div>
            </div>
            <div class="movement-draft-fields">
              <label class="field-group movement-draft-control movement-draft-qty">
                <span>Cantidad</span>
                <InputNumber
                  v-model="draft.cantidad"
                  :min="0"
                  :min-fraction-digits="2"
                  :max-fraction-digits="2"
                  input-class="erp-number-input"
                />
              </label>
              <label class="field-group movement-draft-control movement-draft-cost">
                <span>{{ mode === "ingreso" ? `Costo (${draftCurrencyLabel})` : `Costo ref. (${draftCurrencyLabel})` }}</span>
                <InputNumber
                  v-if="canEditDraftCost"
                  v-model="draft.costo_unitario"
                  :min="0"
                  :min-fraction-digits="2"
                  :max-fraction-digits="2"
                  input-class="erp-number-input"
                />
                <div v-else class="movement-readonly-cost">
                  <strong>{{ selectedCurrencySymbol }} {{ formatMoney(draft.costo_unitario) }}</strong>
                  <small>{{ costLockMessage }}</small>
                </div>
              </label>
              <Button type="button" class="movement-draft-add" icon="bi bi-plus-lg" label="Agregar" @click="appendDraftItem" />
            </div>
          </div>

          <div class="movement-items-table">
            <DataTable :value="items" class="movements-table" responsive-layout="scroll" size="small">
              <Column header="Producto">
                <template #body="{ data }">
                  <div class="products-main-cell">
                    <strong>{{ data.descripcion }}</strong>
                    <small>{{ data.cod_producto }}</small>
                  </div>
                </template>
              </Column>
              <Column header="Cantidad">
                <template #body="{ data }">{{ formatQty(data.cantidad) }}</template>
              </Column>
              <Column header="Costo">
                <template #body="{ data }">
                  <div class="movement-money-cell">
                    <strong>{{ selectedCurrencySymbol }} {{ formatMoney(data.costo_unitario) }}</strong>
                    <small v-if="itemEquivalentLabel(data, 'unit')">{{ itemEquivalentLabel(data, "unit") }}</small>
                  </div>
                </template>
              </Column>
              <Column header="Subtotal">
                <template #body="{ data }">
                  <div class="movement-money-cell">
                    <strong>{{ selectedCurrencySymbol }} {{ formatMoney(itemSubtotal(data)) }}</strong>
                    <small v-if="itemEquivalentLabel(data, 'subtotal')">{{ itemEquivalentLabel(data, "subtotal") }}</small>
                  </div>
                </template>
              </Column>
              <Column header="Acciones">
                <template #body="{ index }">
                  <Button
                    type="button"
                    icon="bi bi-trash3"
                    severity="danger"
                    variant="text"
                    rounded
                    @click="removeItem(index)"
                  />
                </template>
              </Column>
              <template #empty>
                <div class="empty-state">Aun no hay productos agregados.</div>
              </template>
            </DataTable>
          </div>

          <div class="movement-totals">
            <div class="movement-total-box">
              <span>Total {{ selectedCurrencyCode }}</span>
              <strong>{{ selectedCurrencySymbol }} {{ formatMoney(totalInSelectedCurrency) }}</strong>
            </div>
            <div class="movement-total-box">
              <span>Equiv. C$</span>
              <strong>{{ baseCurrencySymbol }} {{ formatMoney(totalCs) }}</strong>
            </div>
            <div class="movement-total-box">
              <span>Equiv. USD</span>
              <strong>US$ {{ formatMoney(totalUsd) }}</strong>
            </div>
          </div>

          <p v-if="formError" class="auth-error">{{ formError }}</p>
          <p v-if="successMessage" class="settings-feedback settings-feedback-success">
            <i class="bi bi-check-circle-fill"></i>
            <span>{{ successMessage }}</span>
          </p>

          <div class="movement-form-actions">
            <Button type="button" severity="secondary" variant="outlined" @click="resetMovementForm">
              Limpiar
            </Button>
            <Button :loading="submitting" type="submit">
              {{ submitting ? "Guardando..." : mode === "ingreso" ? "Registrar ingreso" : "Registrar egreso" }}
            </Button>
          </div>
        </form>
      </section>

    </div>

    <section v-else class="panel-card movement-history-card movement-history-section">
      <div class="movement-card-head">
        <div>
          <span class="products-section-kicker">Historico documental</span>
          <h3>Movimientos registrados</h3>
          <p>Consulta documentos por tipo de movimiento, motivo y rango de fecha.</p>
        </div>
        <div class="enterprise-table-actions">
          <Tag severity="contrast" :value="`${filteredHistory.length} registros`" rounded />
          <Button
            type="button"
            icon="bi bi-file-earmark-excel"
            label="Exportar"
            severity="secondary"
            variant="outlined"
            size="small"
            @click="exportMovementHistory"
          />
        </div>
      </div>

      <div class="movement-history-filters">
        <label class="field-group">
          <span>Movimiento</span>
          <select v-model="historyKindFilter" class="form-control">
            <option value="all">Todos</option>
            <option value="INGRESO">Ingresos</option>
            <option value="EGRESO">Egresos</option>
          </select>
        </label>
        <label class="field-group">
          <span>Tipo</span>
          <Select
            v-model="historyTypeFilter"
            :options="historyTypeOptions"
            option-label="nombre"
            option-value="history_key"
            placeholder="Todos los tipos"
            filter
            show-clear
          />
        </label>
        <label class="field-group">
          <span>Desde</span>
          <span class="enterprise-date-input">
            <DatePicker
              v-model="historyDateFrom"
              class="enterprise-date-picker"
              date-format="dd-mm-yy"
              placeholder="Desde"
            />
            <i class="bi bi-calendar3"></i>
          </span>
        </label>
        <label class="field-group">
          <span>Hasta</span>
          <span class="enterprise-date-input">
            <DatePicker
              v-model="historyDateTo"
              class="enterprise-date-picker"
              date-format="dd-mm-yy"
              placeholder="Hasta"
            />
            <i class="bi bi-calendar3"></i>
          </span>
        </label>
        <Button type="button" severity="secondary" variant="outlined" icon="bi bi-eraser" label="Limpiar filtros" @click="clearHistoryFilters" />
      </div>

      <DataTable
        ref="movementHistoryTable"
        :value="filteredHistory"
        class="movements-table movement-history-table"
        paginator
        :rows="12"
        :rows-per-page-options="[12, 25, 50, 100]"
        paginator-template="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink RowsPerPageDropdown CurrentPageReport"
        current-page-report-template="{first}-{last} de {totalRecords}"
        responsive-layout="scroll"
        scrollable
        scroll-height="560px"
        resizable-columns
        column-resize-mode="fit"
        removable-sort
        striped-rows
        export-filename="historico-inventario"
        size="small"
      >
        <Column field="documento" header="Doc." sortable>
          <template #body="{ data }">{{ data.documento }}</template>
        </Column>
        <Column field="fecha" header="Fecha" sortable>
          <template #body="{ data }">{{ formatDisplayDate(data.fecha) }}</template>
        </Column>
        <Column field="kind" header="Movimiento" sortable>
          <template #body="{ data }">
            <Tag :severity="data.kind === 'INGRESO' ? 'success' : 'warn'" :value="data.kind" rounded />
          </template>
        </Column>
        <Column field="tipo_nombre" header="Tipo" sortable>
          <template #body="{ data }">{{ data.tipo_nombre }}</template>
        </Column>
        <Column field="bodega_nombre" header="Bodega" sortable>
          <template #body="{ data }">{{ data.bodega_nombre }}</template>
        </Column>
        <Column field="items_preview" header="Detalle">
          <template #body="{ data }">
            <div class="movement-history-detail">
              <strong>{{ data.items_count }} items</strong>
              <span>{{ data.items_preview }}</span>
            </div>
          </template>
        </Column>
        <Column field="total_cs" header="Total" sortable>
          <template #body="{ data }">{{ baseCurrencySymbol }} {{ formatMoney(data.total_cs) }}</template>
        </Column>
        <Column header="Reporte" frozen align-frozen="right">
          <template #body="{ data }">
            <Button
              type="button"
              icon="bi bi-file-earmark-pdf"
              severity="secondary"
              variant="text"
              rounded
              aria-label="Ver reporte"
              @click="openMovementReport(data)"
            />
          </template>
        </Column>
        <template #empty>
          <div class="empty-state">No hay movimientos para los filtros seleccionados.</div>
        </template>
      </DataTable>
    </section>

    <Dialog v-model:visible="reportDialog" modal :style="{ width: 'min(760px, 94vw)' }" class="movement-report-dialog">
      <template #header>
        <div class="sales-payment-title">
          <span class="products-section-kicker">Reporte de inventario</span>
          <h3>{{ selectedReport?.documento || "Movimiento" }}</h3>
        </div>
      </template>

      <article v-if="selectedReport" class="movement-report">
        <header class="movement-report-head">
          <div>
            <span>{{ businessSettings.trade_name || businessSettings.business_name || "Orange Tec" }}</span>
            <strong>{{ selectedReport.kind === "INGRESO" ? "Reporte de ingreso" : "Reporte de egreso" }}</strong>
            <small>Documento {{ selectedReport.documento }}</small>
          </div>
          <Tag :severity="selectedReport.kind === 'INGRESO' ? 'success' : 'warn'" :value="selectedReport.kind" rounded />
        </header>

        <section class="movement-report-meta">
          <div><span>Fecha</span><strong>{{ formatDisplayDate(selectedReport.fecha) }}</strong></div>
          <div><span>Tipo</span><strong>{{ selectedReport.tipo_nombre }}</strong></div>
          <div><span>Bodega</span><strong>{{ selectedReport.bodega_nombre }}</strong></div>
          <div v-if="selectedReport.bodega_destino_nombre"><span>Bodega destino</span><strong>{{ selectedReport.bodega_destino_nombre }}</strong></div>
          <div v-if="selectedReport.proveedor_nombre"><span>Proveedor</span><strong>{{ selectedReport.proveedor_nombre }}</strong></div>
          <div><span>Moneda</span><strong>{{ selectedReport.moneda }}</strong></div>
          <div><span>Tasa</span><strong>C$ {{ formatMoney(selectedReport.tasa_cambio || exchangeRate) }}</strong></div>
          <div><span>Usuario</span><strong>{{ selectedReport.usuario_registro || "-" }}</strong></div>
        </section>

        <section class="movement-report-lines">
          <div class="movement-report-line movement-report-line-head">
            <span>Producto</span>
            <span>Cantidad</span>
            <span>Costo</span>
            <span>Total</span>
          </div>
          <div v-for="item in selectedReport.items" :key="item.id" class="movement-report-line">
            <span>
              <strong>{{ item.descripcion }}</strong>
              <small>{{ item.cod_producto }}</small>
            </span>
            <span>{{ formatQty(item.cantidad) }}</span>
            <span>C$ {{ formatMoney(item.costo_unitario_cs) }}</span>
            <span>C$ {{ formatMoney(item.subtotal_cs) }}</span>
          </div>
        </section>

        <section class="movement-report-totals">
          <div><span>Total C$</span><strong>C$ {{ formatMoney(selectedReport.total_cs) }}</strong></div>
          <div><span>Total USD</span><strong>US$ {{ formatMoney(selectedReport.total_usd) }}</strong></div>
          <div><span>Items</span><strong>{{ selectedReport.items.length }}</strong></div>
        </section>

        <footer class="movement-report-footer">
          <strong>Afectacion de inventario:</strong>
          <span>{{ selectedReport.kind === "INGRESO" ? "Aumenta existencia del producto en la bodega seleccionada." : "Disminuye existencia del producto en la bodega seleccionada." }}</span>
          <small v-if="selectedReport.observacion">Observacion: {{ selectedReport.observacion }}</small>
        </footer>
      </article>

      <template #footer>
        <div class="sales-payment-footer">
          <Button type="button" severity="secondary" variant="outlined" label="Cerrar" @click="reportDialog = false" />
          <Button type="button" icon="bi bi-printer" label="Imprimir / PDF" @click="printMovementReport" />
        </div>
      </template>
    </Dialog>
  </section>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from "vue";
import Button from "primevue/button";
import Column from "primevue/column";
import DataTable from "primevue/datatable";
import DatePicker from "primevue/datepicker";
import Dialog from "primevue/dialog";
import InputNumber from "primevue/inputnumber";
import InputText from "primevue/inputtext";
import Select from "primevue/select";
import Tag from "primevue/tag";
import { useConfirm } from "primevue/useconfirm";
import { useToast } from "primevue/usetoast";

import { readStoredUser } from "../../services/auth";
import { fetchCurrentExchangeRate, readStoredBusinessSettings } from "../../services/settings";
import {
  createProveedor,
  createEgreso,
  createIngreso,
  fetchEgresos,
  fetchIngresos,
  fetchInventoryCatalogs,
  fetchProducts,
  searchInventoryProducts,
} from "../../services/inventory";

const currentUser = readStoredUser();
const activeSection = ref("ingreso");
const mode = ref("ingreso");
const historyKindFilter = ref("all");
const historyTypeFilter = ref(null);
const historyDateFrom = ref(null);
const historyDateTo = ref(null);
const submitting = ref(false);
const searchingProducts = ref(false);
const formError = ref("");
const successMessage = ref("");
const savingQuickProvider = ref(false);
const showQuickProvider = ref(false);
const reportDialog = ref(false);
const selectedReport = ref(null);
const movementHistoryTable = ref(null);
const movementDatePickerRef = ref(null);
const movementDatePickerOpen = ref(false);
const movementDateViewDate = ref(new Date());
const searchQuery = ref("");
const searchResults = ref([]);
const searchActiveIndex = ref(-1);
const searchResultButtons = ref([]);
const ingresos = ref([]);
const egresos = ref([]);
const products = ref([]);
const searchTimeout = ref(null);
const catalogs = reactive({
  bodegas: [],
  proveedores: [],
  ingreso_tipos: [],
  egreso_tipos: [],
});
const form = reactive(getEmptyMovementForm());
const draft = reactive(getEmptyDraft());
const items = ref([]);
const quickProvider = reactive({
  nombre: "",
  tipo: "",
  activo: true,
});
const DRAFT_STORAGE_KEY = "erp_inventory_movement_draft_v1";
const businessSettings = readStoredBusinessSettings() || {};
const confirm = useConfirm();
const toast = useToast();

const baseCurrencySymbol = "C$";
const selectedCurrencyCode = computed(() => (form.moneda === "USD" ? "USD" : "CS"));
const selectedCurrencySymbol = computed(() => (form.moneda === "USD" ? "US$" : "C$"));
const exchangeRate = computed(() => Number(form.tasa_cambio || 0));
const inventoryCostCurrency = computed(() => {
  if (businessSettings?.inventory_cs_only) return "CS";
  return (businessSettings?.pricing_currency || "CS").toUpperCase() === "USD" ? "USD" : "CS";
});
const movementTypeOptions = computed(() => (mode.value === "ingreso" ? catalogs.ingreso_tipos : catalogs.egreso_tipos));
const historyTypeOptions = computed(() => {
  const ingresoOptions = catalogs.ingreso_tipos.map((item) => ({
    ...item,
    history_key: `INGRESO:${item.id}`,
    nombre: historyKindFilter.value === "all" ? `Ingreso - ${item.nombre}` : item.nombre,
  }));
  const egresoOptions = catalogs.egreso_tipos.map((item) => ({
    ...item,
    history_key: `EGRESO:${item.id}`,
    nombre: historyKindFilter.value === "all" ? `Egreso - ${item.nombre}` : item.nombre,
  }));
  if (historyKindFilter.value === "INGRESO") return ingresoOptions;
  if (historyKindFilter.value === "EGRESO") return egresoOptions;
  return [
    ...ingresoOptions,
    ...egresoOptions,
  ];
});
const selectedIngresoType = computed(() => catalogs.ingreso_tipos.find((item) => item.id === form.tipo_id) || null);
const selectedEgresoType = computed(() => catalogs.egreso_tipos.find((item) => item.id === form.tipo_id) || null);
const requiresProvider = computed(() => mode.value === "ingreso" && Boolean(selectedIngresoType.value?.requiere_proveedor));
const canEditDraftCost = computed(() => {
  const typeName = String(selectedIngresoType.value?.nombre || "").toLowerCase();
  return mode.value === "ingreso" && /compras?/.test(typeName) && /local(es)?/.test(typeName);
});
const costLockMessage = computed(() =>
  mode.value === "egreso"
    ? "Costo del producto bloqueado"
    : "Editable solo en compras locales",
);
const showDestinationBodega = computed(
  () =>
    mode.value === "egreso" &&
    /traslado/i.test(selectedEgresoType.value?.nombre || ""),
);
const destinationBodegas = computed(() => catalogs.bodegas.filter((item) => item.id !== form.bodega_id));
const productMap = computed(() => {
  const map = new Map();
  products.value.forEach((item) => map.set(item.id, item));
  return map;
});
const movementTotalCs = computed(
  () =>
    [...ingresos.value, ...egresos.value].reduce((sum, item) => sum + Number(item.total_cs || 0), 0),
);

async function applyCurrentExchangeRate() {
  if (Number(form.tasa_cambio || 0) > 0) return;
  try {
    const currentRate = await fetchCurrentExchangeRate();
    if (currentRate?.rate) {
      form.tasa_cambio = Number(currentRate.rate);
    }
  } catch {
    form.tasa_cambio = form.tasa_cambio || null;
  }
}
const totalInSelectedCurrency = computed(() =>
  items.value.reduce((sum, item) => sum + itemSubtotal(item), 0),
);
const totalCs = computed(() => {
  const total = totalInSelectedCurrency.value;
  if (form.moneda === "CS") return total;
  const rate = Number(form.tasa_cambio || 0);
  return rate > 0 ? total * rate : 0;
});
const totalUsd = computed(() => {
  const total = totalInSelectedCurrency.value;
  if (form.moneda === "USD") return total;
  const rate = Number(form.tasa_cambio || 0);
  return rate > 0 ? total / rate : 0;
});
const modeCopy = computed(() =>
  mode.value === "ingreso"
    ? "Captura compras, inventario inicial, ajustes y entradas por proveedor."
    : "Registra salidas, mermas, inventario fisico o traslados entre bodegas.",
);
const draftCurrencyLabel = computed(() => (form.moneda === "USD" ? "USD" : "C$"));
const draftEquivalentText = computed(() => {
  const value = Number(draft.costo_unitario || 0);
  if (value <= 0) return "";
  const equivalent = form.moneda === "USD"
    ? convertAmount(value, "USD", "CS")
    : convertAmount(value, "CS", "USD");
  if (equivalent <= 0) return "";
  return form.moneda === "USD"
    ? `C$ ${formatMoney(equivalent)}`
    : `US$ ${formatMoney(equivalent)}`;
});
const combinedHistory = computed(() => {
  const productLookup = productMap.value;
  const ingresoTipos = new Map(catalogs.ingreso_tipos.map((item) => [item.id, item.nombre]));
  const egresoTipos = new Map(catalogs.egreso_tipos.map((item) => [item.id, item.nombre]));
  const bodegas = new Map(catalogs.bodegas.map((item) => [item.id, item.name]));
  const proveedores = new Map(catalogs.proveedores.map((item) => [item.id, item.nombre]));

  const toPreview = (movementItems) =>
    movementItems
      .slice(0, 3)
      .map((item) => productLookup.get(item.producto_id)?.descripcion || `#${item.producto_id}`)
      .join(", ");

  return [
    ...ingresos.value.map((item) => ({
      id: item.id,
      documento: `ING-${item.id}`,
      fecha: item.fecha,
      kind: "INGRESO",
      tipo_id: item.tipo_id,
      history_type_key: `INGRESO:${item.tipo_id}`,
      tipo_nombre: ingresoTipos.get(item.tipo_id) || "Ingreso",
      bodega_nombre: bodegas.get(item.bodega_id) || "-",
      proveedor_nombre: proveedores.get(item.proveedor_id) || "",
      moneda: item.moneda || "CS",
      tasa_cambio: item.tasa_cambio,
      total_cs: Number(item.total_cs || 0),
      total_usd: Number(item.total_usd || 0),
      observacion: item.observacion || "",
      usuario_registro: item.usuario_registro || "",
      items_count: item.items.length,
      items_preview: toPreview(item.items),
      raw: item,
    })),
    ...egresos.value.map((item) => ({
      id: item.id,
      documento: `EGR-${item.id}`,
      fecha: item.fecha,
      kind: "EGRESO",
      tipo_id: item.tipo_id,
      history_type_key: `EGRESO:${item.tipo_id}`,
      tipo_nombre: egresoTipos.get(item.tipo_id) || "Egreso",
      bodega_nombre: bodegas.get(item.bodega_id) || "-",
      bodega_destino_nombre: bodegas.get(item.bodega_destino_id) || "",
      moneda: item.moneda || "CS",
      tasa_cambio: item.tasa_cambio,
      total_cs: Number(item.total_cs || 0),
      total_usd: Number(item.total_usd || 0),
      observacion: item.observacion || "",
      usuario_registro: item.usuario_registro || "",
      items_count: item.items.length,
      items_preview: toPreview(item.items),
      raw: item,
    })),
  ].sort((a, b) => `${b.fecha}-${b.id}`.localeCompare(`${a.fecha}-${a.id}`));
});
const filteredHistory = computed(() =>
  combinedHistory.value.filter((item) => {
    const fromIso = historyDateFrom.value ? toIsoDate(historyDateFrom.value) : "";
    const toIso = historyDateTo.value ? toIsoDate(historyDateTo.value) : "";
    if (historyKindFilter.value !== "all" && item.kind !== historyKindFilter.value) return false;
    if (historyTypeFilter.value && item.history_type_key !== historyTypeFilter.value) return false;
    if (fromIso && item.fecha < fromIso) return false;
    if (toIso && item.fecha > toIso) return false;
    return true;
  }),
);
const formattedMovementDate = computed(() => formatDisplayDate(form.fecha));
const movementDateWeekdays = ["Do", "Lu", "Ma", "Mi", "Ju", "Vi", "Sa"];
const movementDateMonthLabel = computed(() =>
  new Intl.DateTimeFormat("es-NI", {
    month: "long",
    year: "numeric",
  }).format(movementDateViewDate.value),
);
const movementDateCalendarDays = computed(() => buildMovementDateCalendar(movementDateViewDate.value, form.fecha));

function getEmptyMovementForm() {
  return {
    tipo_id: null,
    bodega_id: null,
    bodega_destino_id: null,
    proveedor_id: null,
    fecha: todayIsoDate(),
    moneda: "CS",
    tasa_cambio: null,
    observacion: "",
    usuario_registro: currentUser?.email || "sistema",
  };
}

function getEmptyDraft() {
  return {
    product_id: null,
    cod_producto: "",
    descripcion: "",
    existencia: 0,
    cantidad: 1,
    costo_unitario: 0,
  };
}

function resetDraft() {
  Object.assign(draft, getEmptyDraft());
  searchQuery.value = "";
  searchResults.value = [];
  searchActiveIndex.value = -1;
  searchResultButtons.value = [];
}

function resetQuickProvider() {
  quickProvider.nombre = "";
  quickProvider.tipo = "";
  quickProvider.activo = true;
}

function resetMovementForm() {
  Object.assign(form, getEmptyMovementForm());
  items.value = [];
  formError.value = "";
  successMessage.value = "";
  showQuickProvider.value = false;
  resetQuickProvider();
  resetDraft();
  if (mode.value === "ingreso") {
    const localProvider = catalogs.proveedores.find((item) => /local/i.test(item.nombre || ""));
    if (localProvider) {
      form.proveedor_id = localProvider.id;
    }
  }
}

function todayIsoDate() {
  return toIsoDate(new Date());
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

function buildMovementDateCalendar(viewDate, selectedIso) {
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

function toggleMovementDatePicker() {
  movementDateViewDate.value = parseIsoDate(form.fecha);
  movementDatePickerOpen.value = !movementDatePickerOpen.value;
}

function moveMovementDateMonth(direction) {
  const nextDate = new Date(movementDateViewDate.value);
  nextDate.setMonth(nextDate.getMonth() + direction);
  movementDateViewDate.value = nextDate;
}

function selectMovementDate(isoDate) {
  form.fecha = isoDate;
  movementDateViewDate.value = parseIsoDate(isoDate);
  movementDatePickerOpen.value = false;
}

function handleMovementDateOutsideClick(event) {
  if (!movementDatePickerOpen.value) return;
  const root = movementDatePickerRef.value;
  if (root && !root.contains(event.target)) {
    movementDatePickerOpen.value = false;
  }
}

function switchMode(nextMode) {
  activeSection.value = nextMode;
  mode.value = nextMode;
  resetMovementForm();
}

function clearHistoryFilters() {
  historyKindFilter.value = "all";
  historyTypeFilter.value = null;
  historyDateFrom.value = null;
  historyDateTo.value = null;
}

function exportMovementHistory() {
  movementHistoryTable.value?.exportCSV();
  toast.add({
    severity: "info",
    summary: "Exportacion iniciada",
    detail: "El historico filtrado se esta descargando en CSV.",
    life: 2600,
  });
}

function formatMoney(value) {
  return new Intl.NumberFormat("es-NI", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(value || 0));
}

function formatQty(value) {
  return Number(value || 0).toFixed(2);
}

function itemSubtotal(item) {
  return Number(item.cantidad || 0) * Number(item.costo_unitario || 0);
}

function reservedQtyForProduct(productId) {
  return items.value.reduce((sum, item) => {
    if (item.producto_id !== productId) return sum;
    return sum + Number(item.cantidad || 0);
  }, 0);
}

function convertAmount(amount, fromCurrency, toCurrency) {
  const numericAmount = Number(amount || 0);
  const rate = exchangeRate.value;
  if (numericAmount <= 0) return 0;
  if (fromCurrency === toCurrency) return numericAmount;
  if (rate <= 0) return 0;
  if (fromCurrency === "USD" && toCurrency === "CS") return numericAmount * rate;
  if (fromCurrency === "CS" && toCurrency === "USD") return numericAmount / rate;
  return 0;
}

function itemEquivalentLabel(item, kind = "subtotal") {
  const amount = kind === "unit" ? Number(item.costo_unitario || 0) : itemSubtotal(item);
  if (amount <= 0) return "";
  const equivalent = form.moneda === "USD"
    ? convertAmount(amount, "USD", "CS")
    : convertAmount(amount, "CS", "USD");
  if (equivalent <= 0) return "";
  return form.moneda === "USD"
    ? `C$ ${formatMoney(equivalent)}`
    : `US$ ${formatMoney(equivalent)}`;
}

function normalizeCostForForm(rawCost) {
  const cost = Number(rawCost || 0);
  if (cost <= 0) return 0;
  if (inventoryCostCurrency.value === form.moneda) return cost;
  return convertAmount(cost, inventoryCostCurrency.value, form.moneda);
}

function selectProduct(item) {
  const meta = productMap.value.get(item.id);
  draft.product_id = item.id;
  draft.cod_producto = item.cod_producto || "";
  draft.descripcion = item.descripcion || "";
  draft.existencia = Number(item.existencia || 0);
  draft.cantidad = 1;
  draft.costo_unitario = normalizeCostForForm(meta?.costo_producto || 0);
  searchQuery.value = `${item.cod_producto} - ${item.descripcion}`;
  searchResults.value = [];
  searchActiveIndex.value = -1;
  searchResultButtons.value = [];
}

function setSearchResultButton(element, index) {
  if (element) {
    searchResultButtons.value[index] = element;
  }
}

async function scrollSearchResultIntoView(index) {
  await nextTick();
  searchResultButtons.value[index]?.scrollIntoView({
    block: "nearest",
    behavior: "smooth",
  });
}

function moveSearchSelection(direction) {
  if (!searchResults.value.length) {
    return;
  }

  if (searchActiveIndex.value === -1) {
    searchActiveIndex.value = direction > 0 ? 0 : searchResults.value.length - 1;
  } else {
    searchActiveIndex.value =
      (searchActiveIndex.value + direction + searchResults.value.length) % searchResults.value.length;
  }

  void scrollSearchResultIntoView(searchActiveIndex.value);
}

function handleSearchEnter() {
  if (!searchResults.value.length) {
    return;
  }

  if (searchActiveIndex.value === -1) {
    searchActiveIndex.value = 0;
    return;
  }

  selectProduct(searchResults.value[searchActiveIndex.value]);
}

function appendDraftItem() {
  if (!draft.product_id) {
    formError.value = "Selecciona un producto para agregarlo al movimiento.";
    return;
  }
  if (Number(draft.cantidad || 0) <= 0) {
    formError.value = "La cantidad debe ser mayor que cero.";
    return;
  }
  const existing = items.value.find((item) => item.producto_id === draft.product_id);
  const nextQty = Number(draft.cantidad || 0) + (existing ? Number(existing.cantidad || 0) : 0);
  if (mode.value === "egreso" && Number(draft.existencia || 0) < nextQty) {
    const available = Math.max(Number(draft.existencia || 0) - reservedQtyForProduct(draft.product_id), 0);
    formError.value = `Stock insuficiente para ${draft.cod_producto}. Disponible para agregar: ${formatQty(available)}.`;
    return;
  }

  if (existing) {
    existing.cantidad = nextQty;
    if (canEditDraftCost.value) {
      existing.costo_unitario = Number(draft.costo_unitario || 0);
    }
  } else {
    items.value.push({
      producto_id: draft.product_id,
      cod_producto: draft.cod_producto,
      descripcion: draft.descripcion,
      cantidad: Number(draft.cantidad || 0),
      costo_unitario: Number(draft.costo_unitario || 0),
    });
  }
  formError.value = "";
  resetDraft();
}

function clearMovementDraft() {
  try {
    localStorage.removeItem(DRAFT_STORAGE_KEY);
  } catch {
    // ignore local draft errors
  }
}

function productLabel(productId, field) {
  const product = productMap.value.get(productId);
  if (field === "code") return product?.cod_producto || `#${productId}`;
  return product?.descripcion || `Producto #${productId}`;
}

function buildMovementReport(movement, kind) {
  const ingresoTipos = new Map(catalogs.ingreso_tipos.map((item) => [item.id, item.nombre]));
  const egresoTipos = new Map(catalogs.egreso_tipos.map((item) => [item.id, item.nombre]));
  const bodegas = new Map(catalogs.bodegas.map((item) => [item.id, item.name]));
  const proveedores = new Map(catalogs.proveedores.map((item) => [item.id, item.nombre]));
  const isIngreso = kind === "INGRESO";
  return {
    ...movement,
    kind,
    documento: `${isIngreso ? "ING" : "EGR"}-${movement.id}`,
    tipo_nombre: isIngreso
      ? ingresoTipos.get(movement.tipo_id) || "Ingreso"
      : egresoTipos.get(movement.tipo_id) || "Egreso",
    bodega_nombre: bodegas.get(movement.bodega_id) || "-",
    bodega_destino_nombre: bodegas.get(movement.bodega_destino_id) || "",
    proveedor_nombre: proveedores.get(movement.proveedor_id) || "",
    total_cs: Number(movement.total_cs || 0),
    total_usd: Number(movement.total_usd || 0),
    items: (movement.items || []).map((item) => ({
      ...item,
      descripcion: productLabel(item.producto_id, "description"),
      cod_producto: productLabel(item.producto_id, "code"),
      cantidad: Number(item.cantidad || 0),
      costo_unitario_cs: Number(item.costo_unitario_cs || 0),
      costo_unitario_usd: Number(item.costo_unitario_usd || 0),
      subtotal_cs: Number(item.subtotal_cs || 0),
      subtotal_usd: Number(item.subtotal_usd || 0),
    })),
  };
}

function openMovementReport(row) {
  const source = row.raw || (row.kind === "INGRESO"
    ? ingresos.value.find((item) => item.id === row.id)
    : egresos.value.find((item) => item.id === row.id));
  if (!source) return;
  selectedReport.value = buildMovementReport(source, row.kind);
  reportDialog.value = true;
}

function printMovementReport() {
  document.body.classList.add("printing-movement-report");
  window.print();
  window.setTimeout(() => {
    document.body.classList.remove("printing-movement-report");
  }, 500);
}

function removeItem(index) {
  const item = items.value[index];
  confirm.require({
    header: "Quitar producto",
    message: `Confirma quitar ${item?.cod_producto || "este producto"} del movimiento.`,
    icon: "bi bi-trash",
    rejectLabel: "Cancelar",
    acceptLabel: "Quitar",
    acceptClass: "p-button-danger",
    accept: () => {
      items.value.splice(index, 1);
      toast.add({
        severity: "info",
        summary: "Producto removido",
        detail: "La linea fue retirada del documento.",
        life: 2400,
      });
    },
  });
}

function saveMovementDraft() {
  try {
    const payload = {
      mode: mode.value,
      form: {
        tipo_id: form.tipo_id,
        bodega_id: form.bodega_id,
        bodega_destino_id: form.bodega_destino_id,
        proveedor_id: form.proveedor_id,
        fecha: form.fecha,
        moneda: form.moneda,
        tasa_cambio: form.tasa_cambio,
        observacion: form.observacion,
      },
      items: items.value,
    };
    localStorage.setItem(DRAFT_STORAGE_KEY, JSON.stringify(payload));
  } catch {
    // ignore local draft errors
  }
}

function restoreMovementDraft() {
  try {
    const raw = localStorage.getItem(DRAFT_STORAGE_KEY);
    if (!raw) return;
    const draftPayload = JSON.parse(raw);
    if (!draftPayload || draftPayload.mode !== mode.value) return;
    Object.assign(form, {
      ...getEmptyMovementForm(),
      ...draftPayload.form,
      usuario_registro: currentUser?.email || "sistema",
    });
    items.value = Array.isArray(draftPayload.items) ? [...draftPayload.items] : [];
  } catch {
    // ignore malformed draft
  }
}

async function submitQuickProvider() {
  formError.value = "";
  if (!(quickProvider.nombre || "").trim()) {
    formError.value = "El nombre del proveedor es requerido.";
    return;
  }
  savingQuickProvider.value = true;
  try {
    const payload = await createProveedor({
      nombre: quickProvider.nombre.trim(),
      tipo: (quickProvider.tipo || "").trim() || null,
      activo: Boolean(quickProvider.activo),
    });
    catalogs.proveedores = [...catalogs.proveedores, payload].sort((a, b) => (a.nombre || "").localeCompare(b.nombre || ""));
    form.proveedor_id = payload.id;
    showQuickProvider.value = false;
    resetQuickProvider();
    successMessage.value = "Proveedor creado y seleccionado.";
    toast.add({
      severity: "success",
      summary: "Proveedor creado",
      detail: "El proveedor fue seleccionado para este ingreso.",
      life: 2800,
    });
  } catch (err) {
    formError.value = err.message || "No se pudo guardar el proveedor.";
    toast.add({
      severity: "error",
      summary: "No se pudo guardar proveedor",
      detail: formError.value,
      life: 4200,
    });
  } finally {
    savingQuickProvider.value = false;
  }
}

async function loadMovementData() {
  const [catalogData, productData, ingresosData, egresosData] = await Promise.all([
    fetchInventoryCatalogs(),
    fetchProducts("", true),
    fetchIngresos(),
    fetchEgresos(),
  ]);
  catalogs.bodegas = catalogData.bodegas || [];
  catalogs.proveedores = catalogData.proveedores || [];
  catalogs.ingreso_tipos = catalogData.ingreso_tipos || [];
  catalogs.egreso_tipos = catalogData.egreso_tipos || [];
  products.value = productData || [];
  ingresos.value = ingresosData || [];
  egresos.value = egresosData || [];
  resetMovementForm();
  restoreMovementDraft();
}

async function submitMovement() {
  formError.value = "";
  successMessage.value = "";

  if (!form.tipo_id) {
    formError.value = `Selecciona un ${mode.value === "ingreso" ? "tipo de ingreso" : "tipo de egreso"}.`;
    return;
  }
  if (!form.bodega_id) {
    formError.value = "Selecciona la bodega del movimiento.";
    return;
  }
  if (requiresProvider.value && !form.proveedor_id) {
    formError.value = "Este tipo de ingreso requiere proveedor.";
    return;
  }
  if (showDestinationBodega.value && !form.bodega_destino_id) {
    formError.value = "Selecciona la bodega destino para este traslado.";
    return;
  }
  if (form.moneda === "USD" && Number(form.tasa_cambio || 0) <= 0) {
    formError.value = "La tasa de cambio es requerida cuando la moneda es USD.";
    return;
  }
  if (!items.value.length) {
    formError.value = "Debes agregar al menos un producto al movimiento.";
    return;
  }

  submitting.value = true;
  try {
    const payload = {
      tipo_id: form.tipo_id,
      bodega_id: form.bodega_id,
      fecha: form.fecha,
      moneda: form.moneda,
      tasa_cambio: Number(form.tasa_cambio || 0) > 0 ? Number(form.tasa_cambio || 0) : null,
      observacion: form.observacion || null,
      usuario_registro: form.usuario_registro,
      items: items.value.map((item) => {
        const base = {
          producto_id: item.producto_id,
          cantidad: Number(item.cantidad || 0),
        };
        return canEditDraftCost.value
          ? { ...base, costo_unitario: Number(item.costo_unitario || 0) }
          : base;
      }),
      ...(mode.value === "ingreso"
        ? {
            proveedor_id: form.proveedor_id,
          }
        : {
            bodega_destino_id: showDestinationBodega.value ? form.bodega_destino_id : null,
          }),
    };

    if (mode.value === "ingreso") {
      const created = await createIngreso(payload);
      selectedReport.value = buildMovementReport(created, "INGRESO");
    } else {
      const created = await createEgreso(payload);
      selectedReport.value = buildMovementReport(created, "EGRESO");
    }

    clearMovementDraft();
    await loadMovementData();
    reportDialog.value = true;
    successMessage.value =
      mode.value === "ingreso"
        ? "Ingreso de inventario registrado correctamente."
        : "Egreso de inventario registrado correctamente.";
    toast.add({
      severity: "success",
      summary: mode.value === "ingreso" ? "Ingreso registrado" : "Egreso registrado",
      detail: "El saldo de inventario fue actualizado y el reporte quedo disponible.",
      life: 3400,
    });
  } catch (err) {
    formError.value = err.message || "No se pudo registrar el movimiento.";
    toast.add({
      severity: "error",
      summary: "No se pudo registrar",
      detail: formError.value,
      life: 4600,
    });
  } finally {
    submitting.value = false;
  }
}

watch(
  () => form.moneda,
  (nextCurrency, previousCurrency) => {
    if (!previousCurrency || previousCurrency === nextCurrency) {
      return;
    }
    if (Number(form.tasa_cambio || 0) <= 0) {
      return;
    }
    items.value = items.value.map((item) => ({
      ...item,
      costo_unitario: convertAmount(item.costo_unitario, previousCurrency, nextCurrency),
    }));
    if (draft.product_id) {
      draft.costo_unitario = convertAmount(draft.costo_unitario, previousCurrency, nextCurrency);
    }
  },
);

watch(
  () => [searchQuery.value, form.bodega_id, mode.value],
  () => {
    if (searchTimeout.value) {
      clearTimeout(searchTimeout.value);
    }
    const query = searchQuery.value.trim();
    if (draft.product_id && query === `${draft.cod_producto} - ${draft.descripcion}`) {
      return;
    }
    if (query.length < 2) {
      searchResults.value = [];
      searchActiveIndex.value = -1;
      searchResultButtons.value = [];
      if (!query) {
        Object.assign(draft, getEmptyDraft());
      }
      return;
    }
    searchTimeout.value = setTimeout(async () => {
      searchingProducts.value = true;
      try {
        const response = await searchInventoryProducts(query, form.bodega_id || null, 1);
        searchResults.value = response.items || [];
        searchActiveIndex.value = searchResults.value.length ? 0 : -1;
        searchResultButtons.value = [];
        if (searchResults.value.length) {
          void scrollSearchResultIntoView(0);
        }
      } catch {
        searchResults.value = [];
        searchActiveIndex.value = -1;
        searchResultButtons.value = [];
      } finally {
        searchingProducts.value = false;
      }
    }, 220);
  },
);

watch(
  () => [mode.value, form.tipo_id],
  () => {
    if (!showDestinationBodega.value) {
      form.bodega_destino_id = null;
    }
    if (mode.value === "ingreso" && !form.proveedor_id) {
      const localProvider = catalogs.proveedores.find((item) => /local/i.test(item.nombre || ""));
      if (localProvider) {
        form.proveedor_id = localProvider.id;
      }
    }
  },
);

watch(
  () => historyKindFilter.value,
  () => {
    historyTypeFilter.value = null;
  },
);

onMounted(async () => {
  try {
    await loadMovementData();
    await applyCurrentExchangeRate();
    document.addEventListener("mousedown", handleMovementDateOutsideClick);
  } catch (err) {
    formError.value = err.message || "No se pudo cargar el modulo de movimientos.";
    toast.add({
      severity: "error",
      summary: "No se pudo cargar inventario",
      detail: formError.value,
      life: 4600,
    });
  }
});

onBeforeUnmount(() => {
  document.removeEventListener("mousedown", handleMovementDateOutsideClick);
  if (searchTimeout.value) clearTimeout(searchTimeout.value);
});

watch(
  () => ({
    mode: mode.value,
    form: {
      tipo_id: form.tipo_id,
      bodega_id: form.bodega_id,
      bodega_destino_id: form.bodega_destino_id,
      proveedor_id: form.proveedor_id,
      fecha: form.fecha,
      moneda: form.moneda,
      tasa_cambio: form.tasa_cambio,
      observacion: form.observacion,
    },
    items: items.value,
  }),
  () => {
    saveMovementDraft();
  },
  { deep: true },
);
</script>
