<!--
  Modulo de compras operativas.
  Hecho por Carlos.
  Colaboracion academica: Oded Garcia y Carlos Ramirez.
  Nota: aqui se manejan insumos internos y solicitudes de cotizacion.
-->
<template>
  <section class="page-section procurement-page">
    <header class="module-hero">
      <div class="module-hero-copy">
        <p class="page-kicker">Compras operativas</p>
        <h1 class="page-title">Insumos y solicitudes de cotizacion</h1>
        <p class="panel-text">
          Controla insumos internos como limpieza, papeleria y mantenimiento, y registra solicitudes de cotizacion sin mezclar mercaderia de venta.
        </p>
      </div>
      <div class="module-hero-meta">
        <div class="module-meta-box">
          <span>Insumos</span>
          <strong>{{ summary.supplies_count }}</strong>
        </div>
        <div class="module-meta-box">
          <span>Bajo stock</span>
          <strong>{{ summary.low_stock_count }}</strong>
        </div>
        <div class="module-meta-box">
          <span>Solicitudes</span>
          <strong>{{ summary.requests_count }}</strong>
        </div>
      </div>
    </header>

    <div class="procurement-tabs">
      <button v-for="tab in tabs" :key="tab.key" type="button" :class="{ active: activeTab === tab.key }" @click="activeTab = tab.key">
        <i class="bi" :class="tab.icon"></i>
        <span>{{ tab.label }}</span>
      </button>
    </div>

    <section v-if="activeTab === 'supplies'" class="panel-card">
      <div class="panel-head">
        <div>
          <span class="products-section-kicker">Inventario interno</span>
          <h3>Insumos de operacion</h3>
        </div>
        <Button icon="bi bi-plus-lg" label="Nuevo insumo" @click="openSupplyDialog()" />
      </div>
      <DataTable :value="supplies" class="enterprise-table" stripedRows paginator :rows="10" responsive-layout="scroll">
        <Column field="code" header="Codigo" sortable />
        <Column field="name" header="Insumo" sortable />
        <Column field="category" header="Categoria" sortable />
        <Column field="unit" header="Unidad" />
        <Column header="Stock">
          <template #body="{ data }">
            <Tag :severity="Number(data.current_stock) <= Number(data.min_stock) ? 'warn' : 'success'" :value="`${formatQty(data.current_stock)} / min ${formatQty(data.min_stock)}`" rounded />
          </template>
        </Column>
        <Column field="location" header="Ubicacion" />
        <Column header="Acciones" style="width: 12rem">
          <template #body="{ data }">
            <div class="table-actions">
              <Button size="small" icon="bi bi-pencil" label="Editar" severity="secondary" variant="outlined" @click="openSupplyDialog(data)" />
              <Button size="small" icon="bi bi-arrow-left-right" severity="secondary" variant="outlined" aria-label="Movimiento" @click="openMovementDialog(data)" />
            </div>
          </template>
        </Column>
      </DataTable>
    </section>

    <section v-else-if="activeTab === 'movements'" class="panel-card">
      <div class="panel-head">
        <div>
          <span class="products-section-kicker">Consumos y entradas</span>
          <h3>Movimientos de insumos</h3>
        </div>
        <Button icon="bi bi-arrow-left-right" label="Nuevo movimiento" @click="openMovementDialog()" />
      </div>
      <DataTable :value="movements" class="enterprise-table" stripedRows paginator :rows="10" responsive-layout="scroll">
        <Column field="fecha" header="Fecha" sortable />
        <Column field="tipo" header="Tipo" sortable>
          <template #body="{ data }">
            <Tag :severity="movementSeverity(data.tipo)" :value="data.tipo" rounded />
          </template>
        </Column>
        <Column field="item_code" header="Codigo" />
        <Column field="item_name" header="Insumo" />
        <Column field="quantity" header="Cantidad" />
        <Column field="area" header="Area" />
        <Column field="requester" header="Solicitante" />
        <Column header="Costo">
          <template #body="{ data }">C$ {{ formatMoney(data.total_cost) }}</template>
        </Column>
      </DataTable>
    </section>

    <section v-else-if="activeTab === 'quotes'" class="panel-card">
      <div class="panel-head">
        <div>
          <span class="products-section-kicker">Cotizaciones</span>
          <h3>Solicitudes de cotizacion</h3>
        </div>
        <Button icon="bi bi-file-earmark-plus" label="Nueva solicitud" @click="openRequestDialog()" />
      </div>
      <DataTable :value="requests" class="enterprise-table" stripedRows paginator :rows="8" responsive-layout="scroll">
        <Column field="number" header="Solicitud" sortable />
        <Column field="fecha" header="Fecha" sortable />
        <Column field="requester" header="Solicitante" />
        <Column field="department" header="Area" />
        <Column field="purpose" header="Necesidad" />
        <Column header="Lineas">
          <template #body="{ data }">{{ data.lines?.length || 0 }}</template>
        </Column>
        <Column header="Cotizaciones">
          <template #body="{ data }">{{ data.quotes?.length || 0 }}</template>
        </Column>
        <Column field="status" header="Estado">
          <template #body="{ data }">
            <Tag :severity="requestSeverity(data.status)" :value="data.status" rounded />
          </template>
        </Column>
        <Column header="Acciones" style="width: 13rem">
          <template #body="{ data }">
            <div class="table-actions">
              <Button size="small" icon="bi bi-pencil" label="Editar" severity="secondary" variant="outlined" @click="openRequestDialog(data)" />
              <Button size="small" icon="bi bi-cash-coin" severity="secondary" variant="outlined" aria-label="Cotizar" @click="openQuoteDialog(data)" />
              <Button size="small" icon="bi bi-envelope" severity="info" variant="outlined" aria-label="Enviar correo" @click="sendRequestByEmail(data)" />
            </div>
          </template>
        </Column>
      </DataTable>
    </section>

    <section v-else-if="activeTab === 'email'" class="panel-card">
      <div class="panel-head">
        <div>
          <span class="products-section-kicker">Notificaciones</span>
          <h3>Correos para solicitudes de cotizacion</h3>
        </div>
      </div>
      <div class="email-settings-grid">
        <form class="email-card" @submit.prevent="submitEmailConfig">
          <h4>Correo emisor</h4>
          <label class="field-group">
            <span>Correo emisor</span>
            <InputText v-model.trim="emailConfig.sender_email" placeholder="compras@empresa.com" />
          </label>
          <label class="field-group">
            <span>Nombre visible</span>
            <InputText v-model.trim="emailConfig.sender_name" placeholder="Compras" />
          </label>
          <label class="products-checkbox">
            <input v-model="emailConfig.active" type="checkbox" />
            <span>Activar envio de correos</span>
          </label>
          <small>SMTP se configura en `.env`: SMTP_USER, SMTP_PASSWORD, SMTP_HOST, SMTP_PORT.</small>
          <Button :loading="saving" type="submit" label="Guardar configuracion" />
        </form>

        <form class="email-card" @submit.prevent="submitRecipient">
          <h4>Agregar destinatario</h4>
          <label class="field-group">
            <span>Correo</span>
            <InputText v-model.trim="recipientForm.email" placeholder="proveedor@dominio.com" />
          </label>
          <label class="field-group">
            <span>Nombre</span>
            <InputText v-model.trim="recipientForm.name" placeholder="Proveedor / Responsable" />
          </label>
          <label class="products-checkbox">
            <input v-model="recipientForm.procurement_quote_active" type="checkbox" />
            <span>Recibe solicitudes de cotizacion</span>
          </label>
          <Button :loading="saving" type="submit" label="Agregar correo" severity="secondary" />
        </form>
      </div>

      <DataTable :value="recipients" class="enterprise-table mt-3" stripedRows paginator :rows="8" responsive-layout="scroll">
        <Column field="email" header="Correo" />
        <Column field="name" header="Nombre" />
        <Column header="Activo">
          <template #body="{ data }">
            <input v-model="data.active" type="checkbox" @change="saveRecipientRow(data)" />
          </template>
        </Column>
        <Column header="Cotizaciones">
          <template #body="{ data }">
            <input v-model="data.procurement_quote_active" type="checkbox" @change="saveRecipientRow(data)" />
          </template>
        </Column>
        <Column header="Acciones" style="width: 8rem">
          <template #body="{ data }">
            <Button size="small" icon="bi bi-save" label="Guardar" severity="secondary" variant="outlined" @click="saveRecipientRow(data)" />
          </template>
        </Column>
      </DataTable>
    </section>

    <Dialog v-model:visible="supplyDialog" modal :header="supplyForm.id ? 'Editar insumo' : 'Nuevo insumo'" :style="{ width: 'min(760px, 94vw)' }">
      <form class="procurement-form-grid" @submit.prevent="submitSupply">
        <label class="field-group">
          <span>Codigo</span>
          <InputText v-model.trim="supplyForm.code" placeholder="Automatico" />
        </label>
        <label class="field-group field-span-2">
          <span>Insumo</span>
          <InputText v-model.trim="supplyForm.name" required placeholder="Cloro, desinfectante, bolsas..." />
        </label>
        <label class="field-group">
          <span>Categoria</span>
          <InputText v-model.trim="supplyForm.category" placeholder="Limpieza" />
        </label>
        <label class="field-group">
          <span>Unidad</span>
          <InputText v-model.trim="supplyForm.unit" />
        </label>
        <label class="field-group">
          <span>Stock minimo</span>
          <InputText v-model.number="supplyForm.min_stock" type="number" min="0" step="0.01" />
        </label>
        <label class="field-group">
          <span>Stock actual</span>
          <InputText v-model.number="supplyForm.current_stock" type="number" min="0" step="0.01" />
        </label>
        <label class="field-group field-span-2">
          <span>Ubicacion</span>
          <InputText v-model.trim="supplyForm.location" />
        </label>
        <label class="products-checkbox">
          <input v-model="supplyForm.active" type="checkbox" />
          <span>Activo</span>
        </label>
      </form>
      <template #footer>
        <Button severity="secondary" variant="outlined" label="Cancelar" @click="supplyDialog = false" />
        <Button :loading="saving" label="Guardar insumo" @click="submitSupply" />
      </template>
    </Dialog>

    <Dialog v-model:visible="movementDialog" modal header="Movimiento de insumo" :style="{ width: 'min(680px, 94vw)' }">
      <form class="procurement-form-grid" @submit.prevent="submitMovement">
        <label class="field-group field-span-2">
          <span>Insumo</span>
          <Select v-model="movementForm.item_id" :options="supplies" option-label="name" option-value="id" filter required />
        </label>
        <label class="field-group">
          <span>Fecha</span>
          <InputText v-model="movementForm.fecha" type="date" />
        </label>
        <label class="field-group">
          <span>Tipo</span>
          <Select v-model="movementForm.tipo" :options="movementTypes" option-label="label" option-value="value" />
        </label>
        <label class="field-group">
          <span>Cantidad</span>
          <InputText v-model.number="movementForm.quantity" type="number" min="0.01" step="0.01" />
        </label>
        <label class="field-group">
          <span>Costo unitario</span>
          <InputText v-model.number="movementForm.unit_cost" type="number" min="0" step="0.01" />
        </label>
        <label class="field-group">
          <span>Area</span>
          <InputText v-model.trim="movementForm.area" />
        </label>
        <label class="field-group">
          <span>Solicitante</span>
          <InputText v-model.trim="movementForm.requester" />
        </label>
      </form>
      <template #footer>
        <Button severity="secondary" variant="outlined" label="Cancelar" @click="movementDialog = false" />
        <Button :loading="saving" label="Guardar movimiento" @click="submitMovement" />
      </template>
    </Dialog>

    <Dialog v-model:visible="requestDialog" modal :header="requestForm.id ? 'Editar solicitud' : 'Nueva solicitud'" :style="{ width: 'min(940px, 96vw)' }">
      <form class="request-editor" @submit.prevent="submitRequest">
        <div class="procurement-form-grid">
          <label class="field-group">
            <span>Fecha</span>
            <InputText v-model="requestForm.fecha" type="date" />
          </label>
          <label class="field-group">
            <span>Necesario para</span>
            <InputText v-model="requestForm.needed_by" type="date" />
          </label>
          <label class="field-group">
            <span>Solicitante</span>
            <InputText v-model.trim="requestForm.requester" required />
          </label>
          <label class="field-group">
            <span>Area</span>
            <InputText v-model.trim="requestForm.department" />
          </label>
          <label class="field-group field-span-2">
            <span>Proposito</span>
            <InputText v-model.trim="requestForm.purpose" required placeholder="Compra de insumos de limpieza para la semana" />
          </label>
          <label class="field-group">
            <span>Estado</span>
            <Select v-model="requestForm.status" :options="requestStatuses" option-label="label" option-value="value" />
          </label>
        </div>

        <div class="request-lines-head">
          <strong>Detalle solicitado</strong>
          <Button type="button" size="small" icon="bi bi-plus" label="Agregar linea" @click="addRequestLine" />
        </div>
        <div class="request-lines">
          <div v-for="(line, index) in requestForm.lines" :key="index" class="request-line-row">
            <label class="field-group request-line-field request-line-supply">
              <span>Insumo</span>
              <Select v-model="line.supply_item_id" :options="supplies" option-label="name" option-value="id" show-clear filter placeholder="Insumo existente" @change="syncLineSupply(line)" />
            </label>
            <label class="field-group request-line-field request-line-description">
              <span>Descripcion</span>
              <InputText v-model.trim="line.description" placeholder="Descripcion del insumo" />
            </label>
            <label class="field-group request-line-field request-line-unit">
              <span>Unidad</span>
              <InputText v-model.trim="line.unit" placeholder="Unidad" />
            </label>
            <label class="field-group request-line-field request-line-quantity">
              <span>Cantidad</span>
              <InputText v-model.number="line.quantity" type="number" min="0.01" step="0.01" />
            </label>
            <label class="field-group request-line-field request-line-cost">
              <span>Costo estimado</span>
              <InputText v-model.number="line.estimated_unit_cost" type="number" min="0" step="0.01" />
            </label>
            <Button class="request-line-remove" type="button" icon="bi bi-trash" severity="danger" variant="outlined" aria-label="Quitar" @click="requestForm.lines.splice(index, 1)" />
          </div>
        </div>
      </form>
      <template #footer>
        <Button severity="secondary" variant="outlined" label="Cancelar" @click="requestDialog = false" />
        <Button :loading="saving" label="Guardar solicitud" @click="submitRequest" />
      </template>
    </Dialog>

    <Dialog v-model:visible="quoteDialog" modal header="Registrar cotizacion de proveedor" :style="{ width: 'min(620px, 94vw)' }">
      <form class="procurement-form-grid" @submit.prevent="submitQuote">
        <label class="field-group field-span-2">
          <span>Proveedor</span>
          <InputText v-model.trim="quoteForm.supplier_name" required />
        </label>
        <label class="field-group">
          <span>Contacto</span>
          <InputText v-model.trim="quoteForm.contact" />
        </label>
        <label class="field-group">
          <span>Monto C$</span>
          <InputText v-model.number="quoteForm.amount_cs" type="number" min="0" step="0.01" />
        </label>
        <label class="field-group">
          <span>Dias entrega</span>
          <InputText v-model.number="quoteForm.delivery_days" type="number" min="0" />
        </label>
        <label class="field-group">
          <span>Condiciones</span>
          <InputText v-model.trim="quoteForm.payment_terms" />
        </label>
      </form>
      <template #footer>
        <Button severity="secondary" variant="outlined" label="Cancelar" @click="quoteDialog = false" />
        <Button :loading="saving" label="Guardar cotizacion" @click="submitQuote" />
      </template>
    </Dialog>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import Button from "primevue/button";
import Column from "primevue/column";
import DataTable from "primevue/datatable";
import Dialog from "primevue/dialog";
import InputText from "primevue/inputtext";
import Select from "primevue/select";
import Tag from "primevue/tag";
import { useToast } from "primevue/usetoast";

import {
  addSupplierQuote,
  createNotificationRecipient,
  createQuoteRequest,
  createSupply,
  createSupplyMovement,
  fetchEmailConfig,
  fetchNotificationRecipients,
  fetchProcurementSummary,
  fetchQuoteRequests,
  fetchSupplies,
  fetchSupplyMovements,
  saveEmailConfig,
  sendQuoteRequestEmail,
  updateNotificationRecipient,
  updateQuoteRequest,
  updateSupply,
} from "../../services/procurement";

const toast = useToast();
const activeTab = ref("supplies");
const saving = ref(false);
const supplies = ref([]);
const movements = ref([]);
const requests = ref([]);
const recipients = ref([]);
const supplyDialog = ref(false);
const movementDialog = ref(false);
const requestDialog = ref(false);
const quoteDialog = ref(false);
const selectedRequest = ref(null);

const summary = reactive({
  supplies_count: 0,
  low_stock_count: 0,
  requests_count: 0,
  pending_requests_count: 0,
  quoted_requests_count: 0,
  total_quoted_cs: 0,
});

const tabs = [
  { key: "supplies", label: "Insumos", icon: "bi-box2-heart" },
  { key: "movements", label: "Movimientos", icon: "bi-arrow-left-right" },
  { key: "quotes", label: "Cotizaciones", icon: "bi-file-earmark-text" },
  { key: "email", label: "Correos", icon: "bi-envelope-at" },
];
const movementTypes = [
  { label: "Ingreso", value: "INGRESO" },
  { label: "Consumo", value: "CONSUMO" },
  { label: "Ajuste", value: "AJUSTE" },
];
const requestStatuses = ["BORRADOR", "SOLICITADA", "COTIZADA", "APROBADA", "RECHAZADA", "CERRADA"].map((value) => ({ label: value, value }));

const supplyForm = reactive(emptySupply());
const movementForm = reactive(emptyMovement());
const requestForm = reactive(emptyRequest());
const quoteForm = reactive(emptyQuote());
const emailConfig = reactive(emptyEmailConfig());
const recipientForm = reactive(emptyRecipient());

function emptySupply() {
  return { id: null, code: "", name: "", category: "Limpieza", unit: "Unidad", min_stock: 0, current_stock: 0, location: "", notes: "", active: true };
}

function emptyMovement() {
  return { item_id: null, fecha: today(), tipo: "INGRESO", quantity: 1, unit_cost: 0, area: "", requester: "", notes: "" };
}

function emptyRequest() {
  return {
    id: null,
    fecha: today(),
    needed_by: "",
    requester: "",
    department: "",
    purpose: "",
    status: "SOLICITADA",
    notes: "",
    lines: [emptyLine()],
  };
}

function emptyLine() {
  return { supply_item_id: null, description: "", unit: "Unidad", quantity: 1, estimated_unit_cost: 0, preferred_supplier: "" };
}

function emptyQuote() {
  return { supplier_name: "", contact: "", amount_cs: 0, delivery_days: null, payment_terms: "", status: "RECIBIDA", notes: "" };
}

function emptyEmailConfig() {
  return { sender_email: "", sender_name: "", active: false };
}

function emptyRecipient() {
  return { email: "", name: "", active: true, procurement_quote_active: true };
}

function today() {
  return new Date().toISOString().slice(0, 10);
}

async function loadData() {
  const [summaryData, supplyData, movementData, requestData, configData, recipientData] = await Promise.all([
    fetchProcurementSummary(),
    fetchSupplies({ include_inactive: true }),
    fetchSupplyMovements(),
    fetchQuoteRequests(),
    fetchEmailConfig(),
    fetchNotificationRecipients(),
  ]);
  Object.assign(summary, summaryData || {});
  supplies.value = supplyData || [];
  movements.value = movementData || [];
  requests.value = requestData || [];
  Object.assign(emailConfig, emptyEmailConfig(), configData || {});
  recipients.value = recipientData || [];
}

function openSupplyDialog(row = null) {
  Object.assign(supplyForm, emptySupply(), row || {});
  supplyDialog.value = true;
}

function openMovementDialog(item = null) {
  Object.assign(movementForm, emptyMovement(), item ? { item_id: item.id } : {});
  movementDialog.value = true;
}

function openRequestDialog(row = null) {
  Object.assign(requestForm, emptyRequest(), row ? {
    ...row,
    lines: (row.lines || []).map((line) => ({ ...emptyLine(), ...line })),
  } : {});
  requestDialog.value = true;
}

function openQuoteDialog(row) {
  selectedRequest.value = row;
  Object.assign(quoteForm, emptyQuote());
  quoteDialog.value = true;
}

async function submitSupply() {
  saving.value = true;
  try {
    const payload = { ...supplyForm };
    if (!payload.code) delete payload.code;
    if (payload.id) await updateSupply(payload.id, payload);
    else await createSupply(payload);
    supplyDialog.value = false;
    await loadData();
    toast.add({ severity: "success", summary: "Insumo guardado", life: 2600 });
  } catch (error) {
    toast.add({ severity: "error", summary: "No se pudo guardar", detail: error.message, life: 4200 });
  } finally {
    saving.value = false;
  }
}

async function submitMovement() {
  saving.value = true;
  try {
    await createSupplyMovement({ ...movementForm });
    movementDialog.value = false;
    await loadData();
    toast.add({ severity: "success", summary: "Movimiento registrado", life: 2600 });
  } catch (error) {
    toast.add({ severity: "error", summary: "No se pudo registrar", detail: error.message, life: 4200 });
  } finally {
    saving.value = false;
  }
}

async function submitRequest() {
  saving.value = true;
  try {
    const payload = {
      ...requestForm,
      needed_by: requestForm.needed_by || null,
      lines: requestForm.lines.filter((line) => line.description && Number(line.quantity) > 0),
    };
    if (payload.id) await updateQuoteRequest(payload.id, payload);
    else await createQuoteRequest(payload);
    requestDialog.value = false;
    await loadData();
    toast.add({ severity: "success", summary: "Solicitud guardada", life: 2600 });
  } catch (error) {
    toast.add({ severity: "error", summary: "No se pudo guardar", detail: error.message, life: 4200 });
  } finally {
    saving.value = false;
  }
}

async function submitQuote() {
  if (!selectedRequest.value) return;
  saving.value = true;
  try {
    await addSupplierQuote(selectedRequest.value.id, { ...quoteForm });
    quoteDialog.value = false;
    await loadData();
    toast.add({ severity: "success", summary: "Cotizacion registrada", life: 2600 });
  } catch (error) {
    toast.add({ severity: "error", summary: "No se pudo guardar", detail: error.message, life: 4200 });
  } finally {
    saving.value = false;
  }
}

async function submitEmailConfig() {
  saving.value = true;
  try {
    await saveEmailConfig({ ...emailConfig });
    await loadData();
    toast.add({ severity: "success", summary: "Correo configurado", life: 2600 });
  } catch (error) {
    toast.add({ severity: "error", summary: "No se pudo guardar", detail: error.message, life: 4200 });
  } finally {
    saving.value = false;
  }
}

async function submitRecipient() {
  saving.value = true;
  try {
    await createNotificationRecipient({ ...recipientForm });
    Object.assign(recipientForm, emptyRecipient());
    await loadData();
    toast.add({ severity: "success", summary: "Destinatario agregado", life: 2600 });
  } catch (error) {
    toast.add({ severity: "error", summary: "No se pudo agregar", detail: error.message, life: 4200 });
  } finally {
    saving.value = false;
  }
}

async function saveRecipientRow(row) {
  try {
    await updateNotificationRecipient(row.id, {
      email: row.email,
      name: row.name,
      active: row.active,
      procurement_quote_active: row.procurement_quote_active,
    });
    toast.add({ severity: "success", summary: "Destinatario actualizado", life: 2200 });
  } catch (error) {
    toast.add({ severity: "error", summary: "No se pudo actualizar", detail: error.message, life: 4200 });
  }
}

async function sendRequestByEmail(row) {
  saving.value = true;
  try {
    const response = await sendQuoteRequestEmail(row.id);
    await loadData();
    toast.add({ severity: "success", summary: "Correo enviado", detail: `${response.recipients.length} destinatario(s).`, life: 3200 });
  } catch (error) {
    toast.add({ severity: "error", summary: "No se pudo enviar", detail: error.message, life: 5200 });
  } finally {
    saving.value = false;
  }
}

function addRequestLine() {
  requestForm.lines.push(emptyLine());
}

function syncLineSupply(line) {
  const item = supplies.value.find((entry) => entry.id === line.supply_item_id);
  if (!item) return;
  line.description = item.name;
  line.unit = item.unit || "Unidad";
}

function formatQty(value) {
  return new Intl.NumberFormat("es-NI", { maximumFractionDigits: 2 }).format(Number(value || 0));
}

function formatMoney(value) {
  return new Intl.NumberFormat("es-NI", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(Number(value || 0));
}

function movementSeverity(value) {
  if (value === "INGRESO") return "success";
  if (value === "CONSUMO") return "warn";
  return "info";
}

function requestSeverity(value) {
  if (value === "APROBADA" || value === "CERRADA") return "success";
  if (value === "RECHAZADA") return "danger";
  if (value === "COTIZADA") return "info";
  return "warn";
}

onMounted(async () => {
  try {
    await loadData();
  } catch (error) {
    toast.add({ severity: "error", summary: "No se pudo cargar compras", detail: error.message, life: 4200 });
  }
});
</script>

<style scoped>
.procurement-tabs {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}

.procurement-tabs button {
  align-items: center;
  background: #fff;
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 8px;
  color: #334155;
  cursor: pointer;
  display: inline-flex;
  font-weight: 700;
  gap: 0.45rem;
  min-height: 2.35rem;
  padding: 0.45rem 0.75rem;
}

.procurement-tabs button.active {
  background: #0f172a;
  border-color: #0f172a;
  color: #fff;
}

.procurement-form-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.8rem;
}

.procurement-form-grid > *,
.request-line-row > * {
  min-width: 0;
}

.request-editor :deep(.p-inputtext),
.request-editor :deep(.p-select),
.request-editor :deep(.p-inputnumber),
.request-editor .form-control {
  width: 100%;
}

.field-span-2 {
  grid-column: span 2;
}

.table-actions {
  display: flex;
  gap: 0.35rem;
  flex-wrap: wrap;
}

.request-editor {
  display: grid;
  gap: 1rem;
}

.request-lines-head {
  align-items: center;
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.request-lines {
  display: grid;
  gap: 0.7rem;
}

.request-line-row {
  align-items: end;
  background: #f8fafc;
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 8px;
  display: grid;
  grid-template-columns:
    minmax(170px, 1.2fr)
    minmax(220px, 1.7fr)
    minmax(92px, 0.65fr)
    minmax(110px, 0.7fr)
    minmax(130px, 0.85fr)
    2.5rem;
  gap: 0.65rem;
  padding: 0.75rem;
}

.request-line-field {
  margin: 0;
}

.request-line-field span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.request-line-remove {
  align-self: end;
  height: 2.55rem;
  width: 2.5rem;
}

.email-settings-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.email-card {
  border: 1px solid rgba(148, 163, 184, 0.35);
  border-radius: 8px;
  display: grid;
  gap: 0.75rem;
  padding: 1rem;
}

.email-card h4 {
  margin: 0;
}

.email-card small {
  color: #64748b;
}

@media (max-width: 900px) {
  .procurement-form-grid,
  .request-line-row,
  .email-settings-grid {
    grid-template-columns: 1fr;
  }

  .field-span-2 {
    grid-column: auto;
  }

  .request-line-remove {
    width: 100%;
  }
}
</style>
