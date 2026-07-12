<!--
  Pantalla de inicio de sesion.
  Hecho por Carlos.
  Colaboracion academica: Oded Garcia y Carlos Ramirez.
  Recordatorio: no dejar credenciales escritas por defecto por seguridad.
-->
<template>
  <div class="auth-page">
    <div class="auth-ambient auth-ambient-one"></div>
    <div class="auth-ambient auth-ambient-two"></div>
    <div class="auth-grid-lines"></div>

    <div class="auth-hero">
      <div class="auth-hero-topline">
        <div class="auth-brand-mark">
          <span class="auth-brand-orbit"></span>
          <span>Orange Tec</span>
        </div>
        <span class="auth-system-status"><i></i> Sistema disponible</span>
      </div>

      <div class="auth-dot-pattern auth-dot-pattern-left"></div>
      <div class="auth-dot-pattern auth-dot-pattern-right"></div>

      <div class="auth-floating-scene" aria-hidden="true">
        <div class="auth-code-card auth-code-card-main">
          <span class="auth-code-card-head"><i></i><i></i><i></i></span>
          <span class="auth-code-line line-long"></span>
          <span class="auth-code-line line-medium"></span>
          <span class="auth-code-line line-short"></span>
          <span class="auth-code-line line-medium"></span>
        </div>
        <div class="auth-code-card auth-code-card-small">
          <span class="auth-chart-bar bar-one"></span>
          <span class="auth-chart-bar bar-two"></span>
          <span class="auth-chart-bar bar-three"></span>
          <span class="auth-chart-bar bar-four"></span>
        </div>
        <span class="auth-orbit auth-orbit-one"></span>
        <span class="auth-orbit auth-orbit-two"></span>
      </div>

      <div class="auth-hero-copy">
        <p class="auth-kicker"><span></span> Sistema empresarial</p>
        <h1>Control total para hacer crecer tu negocio.</h1>
        <p class="auth-copy">
          Centraliza operaciones, inventario y ventas en una plataforma disenada para
          avanzar contigo.
        </p>
        <div class="auth-hero-action">
          <span class="auth-action-line"></span>
          <span>Gestion inteligente, decisiones claras</span>
        </div>
      </div>

      <div class="auth-hero-grid">
        <div class="auth-hero-tile">
          <i class="pi pi-box"></i>
          <div>
            <span>Inventario</span>
            <strong>Control en tiempo real</strong>
          </div>
        </div>
        <div class="auth-hero-tile">
          <i class="pi pi-chart-line"></i>
          <div>
            <span>Ventas</span>
            <strong>Operacion centralizada</strong>
          </div>
        </div>
        <div class="auth-hero-tile">
          <i class="pi pi-shield"></i>
          <div>
            <span>Control</span>
            <strong>Gestion administrativa</strong>
          </div>
        </div>
      </div>
    </div>

    <div class="auth-card">
      <div class="auth-card-glow"></div>
      <div class="auth-card-brand">
        <div v-if="branding.logo_login" class="auth-logo-wrap">
          <img :src="buildAssetUrl(branding.logo_login)" :alt="businessLabel || 'Logo negocio'" />
        </div>
        <div v-else class="auth-logo-fallback">
          <i class="bi bi-buildings"></i>
        </div>
        <div>
          <span>Sistema empresarial</span>
          <strong>{{ businessLabel || "Orange Tec" }}</strong>
        </div>
      </div>

      <div class="auth-card-header">
        <p class="auth-card-eyebrow">Acceso seguro</p>
        <h2>Bienvenido</h2>
        <p>Ingresa tus credenciales para continuar con la gestion del negocio.</p>
      </div>

      <form class="auth-form" autocomplete="off" @submit.prevent="login">
        <label class="field-group">
          <span>Usuario o correo</span>
          <IconField class="auth-input-shell">
            <InputIcon class="bi bi-person" />
            <InputText
              v-model="email"
              class="form-control"
              name="erp_login_user"
              placeholder="Ingresa tu usuario"
              autocomplete="off"
            />
          </IconField>
        </label>

        <label class="field-group">
          <span>Contrasena</span>
          <IconField class="auth-input-shell">
            <InputIcon class="bi bi-shield-lock" />
            <Password
              v-model="password"
              class="form-control"
              input-id="erp-login-password"
              input-name="erp_login_access_key"
              placeholder="Ingresa tu contrasena"
              :feedback="false"
              toggle-mask
              autocomplete="new-password"
            />
          </IconField>
        </label>

        <div class="auth-form-meta">
          <span><i class="bi bi-clock-history"></i> Sesion extendida</span>
          <span><i class="bi bi-lock"></i> Acceso privado</span>
        </div>

        <Button class="auth-submit" :disabled="loading" type="submit" fluid>
          <span>{{ loading ? "Ingresando..." : "Entrar al sistema" }}</span>
          <i v-if="!loading" class="pi pi-arrow-right"></i>
        </Button>

        <p v-if="error" class="auth-error">{{ error }}</p>
      </form>

      <div class="auth-card-footer">
        <span><i class="pi pi-lock"></i> Conexion protegida</span>
        <strong>Orange Tec Sistema empresarial</strong>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import Button from "primevue/button";
import IconField from "primevue/iconfield";
import InputIcon from "primevue/inputicon";
import InputText from "primevue/inputtext";
import Password from "primevue/password";

import { loginUser, storeSession } from "../../services/auth";
import {
  applyBusinessBranding,
  buildAssetUrl,
  fetchPublicBusinessSettings,
  readStoredBusinessSettings,
} from "../../services/settings";

const router = useRouter();
const email = ref("");
const password = ref("");
const error = ref(null);
const loading = ref(false);
const branding = ref(
  readStoredBusinessSettings() || {
    business_name: "Orange Tec",
    trade_name: "Orange Tec",
    logo_login: "",
    logo_favicon: "",
  },
);

const businessLabel = computed(() => branding.value?.trade_name || branding.value?.business_name || "Orange Tec");

async function login() {
  error.value = null;
  loading.value = true;

  try {
    const data = await loginUser({
      email: email.value,
      password: password.value,
    });
    storeSession(data);
    router.push("/app/dashboard");
  } catch (err) {
    error.value = err.message || "No se pudo iniciar sesion";
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  try {
    branding.value = await fetchPublicBusinessSettings();
    applyBusinessBranding(branding.value);
  } catch {
    // Ignore branding errors on login screen.
  }
});
</script>
