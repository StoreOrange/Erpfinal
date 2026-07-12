<!--
  Usuarios, roles y accesos.
  Hecho por Carlos.
  Colaboracion academica: Oded Garcia y Carlos Ramirez.
  Recordatorio: el administrador siempre conserva acceso completo.
-->
<template>
  <section class="page-section users-page access-page">
    <header class="module-hero">
      <div class="module-hero-copy">
        <p class="page-kicker">Seguridad</p>
        <h1 class="page-title">Usuarios, vendedores y accesos</h1>
        <p class="panel-text">
          Gestiona acceso al sistema por sucursal, bodega y perfil operativo, manteniendo vendedores ligados a usuarios.
        </p>
      </div>
      <div class="module-hero-meta">
        <div class="module-meta-box">
          <span>Usuarios</span>
          <strong>{{ users.length }}</strong>
        </div>
        <div class="module-meta-box">
          <span>Vendedores</span>
          <strong>{{ vendors.length }}</strong>
        </div>
        <div class="module-meta-box">
          <span>Sucursales</span>
          <strong>{{ branches.length }}</strong>
        </div>
        <div class="module-meta-box">
          <span>Roles</span>
          <strong>{{ roles.length }}</strong>
        </div>
      </div>
    </header>

    <div class="access-tabs">
      <button v-for="tab in tabs" :key="tab.key" type="button" :class="{ active: activeTab === tab.key }" @click="activeTab = tab.key">
        <i class="bi" :class="tab.icon"></i>
        <span>{{ tab.label }}</span>
      </button>
    </div>

    <section v-if="activeTab === 'users'" class="panel-card access-panel">
      <div class="panel-head">
        <div>
          <span class="products-section-kicker">Control de identidad</span>
          <h3>Usuarios del sistema</h3>
        </div>
        <Button icon="bi bi-person-plus" label="Nuevo usuario" @click="openUserDialog()" />
      </div>
      <DataTable :value="users" class="enterprise-table access-table" stripedRows paginator :rows="8" responsive-layout="scroll">
        <Column field="full_name" header="Usuario" sortable>
          <template #body="{ data }">
            <div class="access-main-cell">
              <strong>{{ data.full_name }}</strong>
              <small>{{ data.email }}</small>
            </div>
          </template>
        </Column>
        <Column header="Roles">
          <template #body="{ data }">
            <Tag v-for="role in data.roles" :key="role.id" class="me-1" severity="info" :value="role.name" rounded />
          </template>
        </Column>
        <Column header="Acceso principal">
          <template #body="{ data }">
            <span>{{ defaultAccessText(data) }}</span>
          </template>
        </Column>
        <Column header="Estado">
          <template #body="{ data }">
            <Tag :severity="data.is_active ? 'success' : 'danger'" :value="data.is_active ? 'Activo' : 'Inactivo'" rounded />
          </template>
        </Column>
        <Column header="Acciones" style="width: 10rem">
          <template #body="{ data }">
            <Button size="small" severity="secondary" variant="outlined" icon="bi bi-pencil" label="Editar" @click="openUserDialog(data)" />
          </template>
        </Column>
        <template #empty>
          <div class="empty-state">No hay usuarios registrados.</div>
        </template>
      </DataTable>
    </section>

    <section v-else-if="activeTab === 'roles'" class="panel-card access-panel">
      <div class="panel-head">
        <div>
          <span class="products-section-kicker">Roles del sistema</span>
          <h3>Permisos por rol</h3>
        </div>
        <Button icon="bi bi-shield-plus" label="Nuevo rol" @click="openRoleDialog()" />
      </div>

      <div class="permission-summary-grid">
        <article v-for="group in permissionGroups" :key="group.key" class="permission-summary">
          <span>{{ group.label }}</span>
          <strong>{{ group.permissions.length }}</strong>
          <small>permisos configurables</small>
        </article>
      </div>

      <DataTable :value="roles" class="enterprise-table access-table" stripedRows paginator :rows="8" responsive-layout="scroll">
        <Column field="name" header="Rol" sortable>
          <template #body="{ data }">
            <div class="access-main-cell">
              <strong>{{ data.name }}</strong>
              <small>{{ roleUserCount(data.name) }} usuario(s) asignado(s)</small>
            </div>
          </template>
        </Column>
        <Column header="Permisos">
          <template #body="{ data }">
            <div class="access-tags">
              <Tag v-for="permission in previewPermissions(data)" :key="permission.name" severity="info" :value="permission.label || permission.name" rounded />
              <Tag v-if="(data.permissions || []).length > 3" severity="secondary" :value="`+${data.permissions.length - 3}`" rounded />
              <span v-if="!(data.permissions || []).length" class="muted-text">Sin permisos</span>
            </div>
          </template>
        </Column>
        <Column header="Cobertura" style="width: 11rem">
          <template #body="{ data }">
            <span>{{ (data.permissions || []).length }} / {{ permissionTotal }}</span>
          </template>
        </Column>
        <Column header="Acciones" style="width: 10rem">
          <template #body="{ data }">
            <Button size="small" severity="secondary" variant="outlined" icon="bi bi-pencil" label="Editar" @click="openRoleDialog(data)" />
          </template>
        </Column>
        <template #empty>
          <div class="empty-state">No hay roles registrados.</div>
        </template>
      </DataTable>
    </section>

    <section v-else-if="activeTab === 'vendors'" class="panel-card access-panel">
      <div class="panel-head">
        <div>
          <span class="products-section-kicker">Catalogo comercial</span>
          <h3>Vendedores</h3>
        </div>
        <Button icon="bi bi-person-badge" label="Nuevo vendedor" @click="openVendorDialog()" />
      </div>
      <DataTable :value="vendors" class="enterprise-table access-table" stripedRows paginator :rows="8" responsive-layout="scroll">
        <Column field="nombre" header="Vendedor" sortable>
          <template #body="{ data }">
            <div class="access-main-cell">
              <strong>{{ data.nombre }}</strong>
              <small>{{ data.code }} · {{ data.user_name || "Sin usuario vinculado" }}</small>
            </div>
          </template>
        </Column>
        <Column field="sucursal_name" header="Sucursal" sortable />
        <Column field="bodega_name" header="Bodega" sortable />
        <Column header="Estado">
          <template #body="{ data }">
            <Tag :severity="data.activo ? 'success' : 'danger'" :value="data.activo ? 'Activo' : 'Inactivo'" rounded />
          </template>
        </Column>
        <Column header="Acciones" style="width: 10rem">
          <template #body="{ data }">
            <Button size="small" severity="secondary" variant="outlined" icon="bi bi-pencil" label="Editar" @click="openVendorDialog(data)" />
          </template>
        </Column>
        <template #empty>
          <div class="empty-state">No hay vendedores registrados.</div>
        </template>
      </DataTable>
    </section>

    <section v-else-if="activeTab === 'branches'" class="panel-card access-panel">
      <div class="panel-head">
        <div>
          <span class="products-section-kicker">Operacion multiubicacion</span>
          <h3>Sucursales</h3>
        </div>
        <Button icon="bi bi-building-add" label="Nueva sucursal" @click="openBranchDialog()" />
      </div>
      <DataTable :value="branches" class="enterprise-table access-table" stripedRows paginator :rows="8" responsive-layout="scroll">
        <Column field="code" header="Codigo" sortable />
        <Column field="name" header="Sucursal" sortable />
        <Column field="phone" header="Telefono" />
        <Column field="address" header="Direccion" />
        <Column header="Estado">
          <template #body="{ data }">
            <Tag :severity="data.activo ? 'success' : 'danger'" :value="data.activo ? 'Activa' : 'Inactiva'" rounded />
          </template>
        </Column>
        <Column header="Acciones" style="width: 10rem">
          <template #body="{ data }">
            <Button size="small" severity="secondary" variant="outlined" icon="bi bi-pencil" label="Editar" @click="openBranchDialog(data)" />
          </template>
        </Column>
      </DataTable>
    </section>

    <section v-else class="panel-card access-panel">
      <div class="panel-head">
        <div>
          <span class="products-section-kicker">Permisos operativos</span>
          <h3>Acceso por sucursal y bodega</h3>
        </div>
        <Button icon="bi bi-shield-plus" label="Nuevo acceso" @click="openProfileDialog()" />
      </div>
      <DataTable :value="accessProfiles" class="enterprise-table access-table" stripedRows paginator :rows="8" responsive-layout="scroll">
        <Column field="user_name" header="Usuario" sortable />
        <Column field="role_scope" header="Perfil" sortable />
        <Column field="sucursal_name" header="Sucursal" />
        <Column field="bodega_name" header="Bodega" />
        <Column header="Permisos">
          <template #body="{ data }">
            <div class="access-tags">
              <Tag v-if="data.can_sell" severity="success" value="Ventas" rounded />
              <Tag v-if="data.can_move_inventory" severity="warn" value="Inventario" rounded />
              <Tag v-if="data.can_manage_catalogs" severity="info" value="Catalogos" rounded />
            </div>
          </template>
        </Column>
        <Column header="Acciones" style="width: 10rem">
          <template #body="{ data }">
            <Button size="small" severity="secondary" variant="outlined" icon="bi bi-pencil" label="Editar" @click="openProfileDialog(data)" />
          </template>
        </Column>
      </DataTable>
    </section>

    <Dialog v-model:visible="userDialog" modal :header="userForm.id ? 'Editar usuario' : 'Nuevo usuario'" class="access-dialog" :style="{ width: 'min(720px, 94vw)' }">
      <form class="access-form-grid" @submit.prevent="submitUser">
        <label class="field-group field-span-2">
          <span>Nombre</span>
          <InputText v-model.trim="userForm.full_name" placeholder="Nombre completo" />
        </label>
        <label class="field-group field-span-2">
          <span>Usuario / email</span>
          <InputText v-model.trim="userForm.email" placeholder="usuario@negocio.com" />
        </label>
        <label class="field-group">
          <span>Clave</span>
          <InputText v-model="userForm.password" type="password" :placeholder="userForm.id ? 'Dejar vacio para no cambiar' : 'Clave inicial'" />
        </label>
        <label class="field-group">
          <span>Roles</span>
          <MultiSelect v-model="userForm.role_names" :options="roleOptions" option-label="label" option-value="value" display="chip" placeholder="Selecciona roles" />
        </label>
        <label class="products-checkbox">
          <input v-model="userForm.is_active" type="checkbox" />
          <span>Usuario activo</span>
        </label>
      </form>
      <template #footer>
        <Button severity="secondary" variant="outlined" label="Cancelar" @click="userDialog = false" />
        <Button :loading="saving" label="Guardar usuario" @click="submitUser" />
      </template>
    </Dialog>

    <Dialog v-model:visible="roleDialog" modal :header="roleForm.id ? 'Editar rol' : 'Nuevo rol'" class="access-dialog" :style="{ width: 'min(920px, 96vw)' }">
      <form class="role-editor" @submit.prevent="submitRole">
        <label class="field-group role-name-field">
          <span>Nombre del rol</span>
          <InputText v-model.trim="roleForm.name" placeholder="supervisor" :disabled="isEditingAdministrator" />
        </label>
        <p v-if="isEditingAdministrator" class="admin-lock-note">
          El administrador mantiene acceso completo por defecto. Sus permisos no se pueden reducir.
        </p>

        <div class="permission-editor-grid">
          <section v-for="group in permissionGroups" :key="group.key" class="permission-group">
            <header>
              <strong>{{ group.label }}</strong>
              <small>{{ selectedInGroup(group) }} / {{ group.permissions.length }}</small>
            </header>
            <label v-for="permission in group.permissions" :key="permission.name" class="permission-check">
              <input v-model="roleForm.permission_names" type="checkbox" :value="permission.name" :disabled="isEditingAdministrator" />
              <span>{{ permission.label || permission.name }}</span>
            </label>
          </section>
        </div>
      </form>
      <template #footer>
        <Button severity="secondary" variant="outlined" label="Cancelar" @click="roleDialog = false" />
        <Button :loading="saving" label="Guardar rol" @click="submitRole" />
      </template>
    </Dialog>

    <Dialog v-model:visible="vendorDialog" modal :header="vendorForm.id ? 'Editar vendedor' : 'Nuevo vendedor'" class="access-dialog" :style="{ width: 'min(780px, 94vw)' }">
      <form class="access-form-grid" @submit.prevent="submitVendor">
        <label class="field-group">
          <span>Codigo</span>
          <InputText v-model.trim="vendorForm.code" placeholder="VEN-002" />
        </label>
        <label class="field-group field-span-2">
          <span>Nombre</span>
          <InputText v-model.trim="vendorForm.nombre" placeholder="Nombre del vendedor" />
        </label>
        <label class="field-group">
          <span>Usuario vinculado</span>
          <Select v-model="vendorForm.user_id" :options="users" option-label="full_name" option-value="id" show-clear filter placeholder="Sin usuario" />
        </label>
        <label class="field-group">
          <span>Sucursal</span>
          <Select v-model="vendorForm.sucursal_id" :options="branches" option-label="name" option-value="id" show-clear filter />
        </label>
        <label class="field-group">
          <span>Bodega</span>
          <Select v-model="vendorForm.bodega_id" :options="bodegas" option-label="name" option-value="id" show-clear filter />
        </label>
        <label class="field-group">
          <span>Telefono</span>
          <InputText v-model.trim="vendorForm.telefono" />
        </label>
        <label class="field-group">
          <span>Email</span>
          <InputText v-model.trim="vendorForm.email" />
        </label>
        <label class="products-checkbox">
          <input v-model="vendorForm.activo" type="checkbox" />
          <span>Vendedor activo</span>
        </label>
      </form>
      <template #footer>
        <Button severity="secondary" variant="outlined" label="Cancelar" @click="vendorDialog = false" />
        <Button :loading="saving" label="Guardar vendedor" @click="submitVendor" />
      </template>
    </Dialog>

    <Dialog v-model:visible="branchDialog" modal :header="branchForm.id ? 'Editar sucursal' : 'Nueva sucursal'" class="access-dialog" :style="{ width: 'min(680px, 94vw)' }">
      <form class="access-form-grid" @submit.prevent="submitBranch">
        <label class="field-group">
          <span>Codigo</span>
          <InputText v-model.trim="branchForm.code" placeholder="SUC-002" />
        </label>
        <label class="field-group field-span-2">
          <span>Nombre</span>
          <InputText v-model.trim="branchForm.name" placeholder="Nombre de sucursal" />
        </label>
        <label class="field-group">
          <span>Telefono</span>
          <InputText v-model.trim="branchForm.phone" />
        </label>
        <label class="field-group field-span-2">
          <span>Direccion</span>
          <InputText v-model.trim="branchForm.address" />
        </label>
        <label class="products-checkbox">
          <input v-model="branchForm.activo" type="checkbox" />
          <span>Sucursal activa</span>
        </label>
      </form>
      <template #footer>
        <Button severity="secondary" variant="outlined" label="Cancelar" @click="branchDialog = false" />
        <Button :loading="saving" label="Guardar sucursal" @click="submitBranch" />
      </template>
    </Dialog>

    <Dialog v-model:visible="profileDialog" modal :header="profileForm.id ? 'Editar acceso' : 'Nuevo acceso'" class="access-dialog" :style="{ width: 'min(760px, 94vw)' }">
      <form class="access-form-grid" @submit.prevent="submitProfile">
        <label class="field-group">
          <span>Usuario</span>
          <Select v-model="profileForm.user_id" :options="users" option-label="full_name" option-value="id" filter />
        </label>
        <label class="field-group">
          <span>Perfil</span>
          <Select v-model="profileForm.role_scope" :options="scopeOptions" option-label="label" option-value="value" />
        </label>
        <label class="field-group">
          <span>Sucursal</span>
          <Select v-model="profileForm.sucursal_id" :options="branches" option-label="name" option-value="id" show-clear filter />
        </label>
        <label class="field-group">
          <span>Bodega</span>
          <Select v-model="profileForm.bodega_id" :options="bodegas" option-label="name" option-value="id" show-clear filter />
        </label>
        <label class="products-checkbox"><input v-model="profileForm.can_sell" type="checkbox" /><span>Puede vender</span></label>
        <label class="products-checkbox"><input v-model="profileForm.can_move_inventory" type="checkbox" /><span>Inventario</span></label>
        <label class="products-checkbox"><input v-model="profileForm.can_manage_catalogs" type="checkbox" /><span>Catalogos</span></label>
        <label class="products-checkbox"><input v-model="profileForm.is_default" type="checkbox" /><span>Acceso principal</span></label>
      </form>
      <template #footer>
        <Button severity="secondary" variant="outlined" label="Cancelar" @click="profileDialog = false" />
        <Button :loading="saving" label="Guardar acceso" @click="submitProfile" />
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
import InputText from "primevue/inputtext";
import MultiSelect from "primevue/multiselect";
import Select from "primevue/select";
import Tag from "primevue/tag";
import { useToast } from "primevue/usetoast";

import {
  createAccessProfile,
  createAccessUser,
  createBranch,
  createRole,
  createVendor,
  fetchAccessUsers,
  fetchBranches,
  fetchPermissions,
  fetchRoles,
  fetchVendors,
  updateAccessProfile,
  updateAccessUser,
  updateBranch,
  updateRole,
  updateVendor,
} from "../../services/access";
import { readStoredUser } from "../../services/auth";
import { fetchInventoryCatalogs } from "../../services/inventory";

const toast = useToast();
const currentUser = readStoredUser();
const activeTab = ref("users");
const saving = ref(false);
const users = ref([]);
const vendors = ref([]);
const branches = ref([]);
const roles = ref([]);
const permissionGroups = ref([]);
const bodegas = ref([]);
const userDialog = ref(false);
const roleDialog = ref(false);
const vendorDialog = ref(false);
const branchDialog = ref(false);
const profileDialog = ref(false);

const tabs = [
  { key: "users", label: "Usuarios", icon: "bi-people" },
  { key: "roles", label: "Roles y permisos", icon: "bi-shield-check" },
  { key: "vendors", label: "Vendedores", icon: "bi-person-badge" },
  { key: "branches", label: "Sucursales", icon: "bi-building" },
  { key: "profiles", label: "Accesos", icon: "bi-shield-lock" },
];

const scopeOptions = [
  { label: "Administrador", value: "ADMINISTRADOR" },
  { label: "Supervisor", value: "SUPERVISOR" },
  { label: "Caja", value: "CAJA" },
  { label: "Vendedor", value: "VENDEDOR" },
  { label: "Inventario", value: "INVENTARIO" },
];

const userForm = reactive(getEmptyUser());
const roleForm = reactive(getEmptyRole());
const vendorForm = reactive(getEmptyVendor());
const branchForm = reactive(getEmptyBranch());
const profileForm = reactive(getEmptyProfile());

const roleOptions = computed(() =>
  roles.value.map((role) => ({ label: role.name, value: role.name })),
);
const currentRole = computed(() => {
  const roleList = currentUser?.roles || [];
  return roleList.length ? roleList[0].name : "Sin rol";
});
const accessProfiles = computed(() => users.value.flatMap((user) => user.access_profiles || []));
const permissionTotal = computed(() => permissionGroups.value.reduce((total, group) => total + group.permissions.length, 0));
const isEditingAdministrator = computed(() => (roleForm.name || "").trim().toLowerCase() === "administrador");

function getEmptyUser() {
  return { id: null, full_name: "", email: "", password: "", is_active: true, role_names: ["vendedor"] };
}

function getEmptyRole() {
  return { id: null, name: "", permission_names: [] };
}

function getEmptyVendor() {
  return { id: null, code: nextVendorCode(), nombre: "", user_id: null, sucursal_id: null, bodega_id: null, telefono: "", email: "", meta_ventas: null, activo: true };
}

function getEmptyBranch() {
  return { id: null, code: nextBranchCode(), name: "", address: "", phone: "", activo: true };
}

function getEmptyProfile() {
  return { id: null, user_id: null, sucursal_id: null, bodega_id: null, role_scope: "VENDEDOR", can_sell: true, can_move_inventory: false, can_manage_catalogs: false, is_default: true, activo: true };
}

function nextVendorCode() {
  return `VEN-${String(vendors.value.length + 1).padStart(3, "0")}`;
}

function nextBranchCode() {
  return `SUC-${String(branches.value.length + 1).padStart(3, "0")}`;
}

function defaultAccessText(user) {
  const profile = (user.access_profiles || []).find((item) => item.is_default) || (user.access_profiles || [])[0];
  if (!profile) return "Sin acceso asignado";
  return `${profile.sucursal_name || "Todas"} / ${profile.bodega_name || "Todas"}`;
}

async function loadData() {
  const [userData, vendorData, branchData, roleData, permissionData, catalogData] = await Promise.all([
    fetchAccessUsers(),
    fetchVendors(true),
    fetchBranches(),
    fetchRoles(),
    fetchPermissions(),
    fetchInventoryCatalogs(),
  ]);
  users.value = userData || [];
  vendors.value = vendorData || [];
  branches.value = branchData || [];
  roles.value = roleData || [];
  permissionGroups.value = permissionData || [];
  bodegas.value = catalogData.bodegas || [];
}

function openUserDialog(row = null) {
  Object.assign(userForm, getEmptyUser(), row
    ? { ...row, password: "", role_names: (row.roles || []).map((role) => role.name) }
    : {});
  userDialog.value = true;
}

function openRoleDialog(row = null) {
  Object.assign(roleForm, getEmptyRole(), row
    ? { ...row, permission_names: (row.permissions || []).map((permission) => permission.name) }
    : {});
  roleDialog.value = true;
}

function openVendorDialog(row = null) {
  Object.assign(vendorForm, getEmptyVendor(), row || {});
  vendorDialog.value = true;
}

function openBranchDialog(row = null) {
  Object.assign(branchForm, getEmptyBranch(), row || {});
  branchDialog.value = true;
}

function openProfileDialog(row = null) {
  Object.assign(profileForm, getEmptyProfile(), row || {});
  profileDialog.value = true;
}

async function submitUser() {
  saving.value = true;
  try {
    const payload = { ...userForm };
    if (!payload.password) delete payload.password;
    if (payload.id) await updateAccessUser(payload.id, payload);
    else await createAccessUser(payload);
    await loadData();
    userDialog.value = false;
    toast.add({ severity: "success", summary: "Usuario guardado", detail: "Acceso actualizado correctamente.", life: 3000 });
  } catch (error) {
    toast.add({ severity: "error", summary: "No se pudo guardar", detail: error.message, life: 4200 });
  } finally {
    saving.value = false;
  }
}

async function submitRole() {
  saving.value = true;
  try {
    const payload = {
      name: roleForm.name,
      permission_names: roleForm.permission_names,
    };
    if (roleForm.id) await updateRole(roleForm.id, payload);
    else await createRole(payload);
    await loadData();
    roleDialog.value = false;
    toast.add({ severity: "success", summary: "Rol guardado", detail: "Permisos del rol actualizados.", life: 3000 });
  } catch (error) {
    toast.add({ severity: "error", summary: "No se pudo guardar", detail: error.message, life: 4200 });
  } finally {
    saving.value = false;
  }
}

async function submitVendor() {
  saving.value = true;
  try {
    const payload = { ...vendorForm };
    if (payload.id) await updateVendor(payload.id, payload);
    else await createVendor(payload);
    await loadData();
    vendorDialog.value = false;
    toast.add({ severity: "success", summary: "Vendedor guardado", detail: "Catalogo comercial actualizado.", life: 3000 });
  } catch (error) {
    toast.add({ severity: "error", summary: "No se pudo guardar", detail: error.message, life: 4200 });
  } finally {
    saving.value = false;
  }
}

async function submitBranch() {
  saving.value = true;
  try {
    const payload = { ...branchForm };
    if (payload.id) await updateBranch(payload.id, payload);
    else await createBranch(payload);
    await loadData();
    branchDialog.value = false;
    toast.add({ severity: "success", summary: "Sucursal guardada", detail: "Estructura operativa actualizada.", life: 3000 });
  } catch (error) {
    toast.add({ severity: "error", summary: "No se pudo guardar", detail: error.message, life: 4200 });
  } finally {
    saving.value = false;
  }
}

async function submitProfile() {
  saving.value = true;
  try {
    const payload = { ...profileForm };
    if (payload.id) await updateAccessProfile(payload.id, payload);
    else await createAccessProfile(payload);
    await loadData();
    profileDialog.value = false;
    toast.add({ severity: "success", summary: "Acceso guardado", detail: "Permisos operativos actualizados.", life: 3000 });
  } catch (error) {
    toast.add({ severity: "error", summary: "No se pudo guardar", detail: error.message, life: 4200 });
  } finally {
    saving.value = false;
  }
}

function previewPermissions(role) {
  return (role.permissions || []).slice(0, 3);
}

function roleUserCount(roleName) {
  return users.value.filter((user) => (user.roles || []).some((role) => role.name === roleName)).length;
}

function selectedInGroup(group) {
  return group.permissions.filter((permission) => roleForm.permission_names.includes(permission.name)).length;
}

onMounted(async () => {
  try {
    await loadData();
  } catch (error) {
    toast.add({ severity: "error", summary: "No se pudo cargar accesos", detail: error.message, life: 4600 });
  }
});
</script>

<style scoped>
.permission-summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.permission-summary {
  border: 1px solid rgba(148, 163, 184, 0.35);
  border-radius: 8px;
  padding: 0.85rem 1rem;
  background: rgba(248, 250, 252, 0.78);
}

.permission-summary span,
.permission-summary small {
  display: block;
  color: #64748b;
  font-size: 0.78rem;
}

.permission-summary strong {
  display: block;
  color: #0f172a;
  font-size: 1.55rem;
  line-height: 1.15;
  margin: 0.15rem 0;
}

.role-editor {
  display: grid;
  gap: 1rem;
}

.role-name-field {
  max-width: 24rem;
}

.admin-lock-note {
  border: 1px solid rgba(14, 116, 144, 0.24);
  border-radius: 8px;
  background: rgba(236, 254, 255, 0.72);
  color: #155e75;
  margin: 0;
  padding: 0.7rem 0.85rem;
  font-size: 0.86rem;
}

.permission-editor-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 0.85rem;
  max-height: min(58vh, 620px);
  overflow: auto;
  padding-right: 0.25rem;
}

.permission-group {
  border: 1px solid rgba(148, 163, 184, 0.42);
  border-radius: 8px;
  background: #ffffff;
  padding: 0.8rem;
}

.permission-group header {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  align-items: center;
  padding-bottom: 0.55rem;
  border-bottom: 1px solid rgba(226, 232, 240, 0.9);
  margin-bottom: 0.55rem;
}

.permission-group header strong {
  color: #0f172a;
  font-size: 0.9rem;
}

.permission-group header small,
.muted-text {
  color: #64748b;
  font-size: 0.78rem;
}

.permission-check {
  display: flex;
  align-items: flex-start;
  gap: 0.55rem;
  padding: 0.42rem 0.2rem;
  color: #334155;
  font-size: 0.86rem;
  line-height: 1.25;
}

.permission-check input {
  width: 1rem;
  height: 1rem;
  margin-top: 0.05rem;
  accent-color: #0f766e;
}
</style>
