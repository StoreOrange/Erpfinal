<!--
  Configuracion general del negocio.
  Hecho por Carlos.
  Colaboracion academica: Oded Garcia y Carlos Ramirez.
  Nota: estos datos se usan en marcas, logos, moneda y documentos del sistema.
-->
<template>
  <section class="page-section settings-page">
    <div class="module-hero">
      <div class="module-hero-copy">
        <p class="page-kicker">Datos y Configuraciones</p>
        <h1 class="page-title">Informacion del Entorno Empresarial</h1>
        <p class="panel-text">
          Unifica identidad corporativa, multiempresa y politicas operativas del negocio
          en una sola ficha administrativa.
        </p>
      </div>

      <div class="module-hero-meta">
        <div class="module-meta-box">
          <span>Negocio</span>
          <strong>{{ settings.trade_name || settings.business_name || "Sin configurar" }}</strong>
        </div>
        <div class="module-meta-box">
          <span>Entornos</span>
          <strong>{{ environments.length }}</strong>
        </div>
        <div class="module-meta-box">
          <span>Politicas</span>
          <strong>{{ enabledPolicies }} activas</strong>
        </div>
      </div>
    </div>

    <div class="settings-workspace">
      <aside class="settings-subnav panel-card">
        <button
          v-for="item in sections"
          :key="item.key"
          type="button"
          class="settings-subnav-item"
          :class="{ active: currentSection === item.key }"
          @click="currentSection = item.key"
        >
          <i class="bi" :class="item.icon"></i>
          <div>
            <strong>{{ item.label }}</strong>
            <span>{{ item.caption }}</span>
          </div>
        </button>
      </aside>

      <div class="settings-panels">
        <div v-if="success" class="settings-feedback settings-feedback-success">
          <i class="bi bi-check-circle-fill"></i>
          <span>{{ success }}</span>
        </div>
        <div v-if="error" class="settings-feedback settings-feedback-error">
          <i class="bi bi-exclamation-circle-fill"></i>
          <span>{{ error }}</span>
        </div>

        <article v-if="currentSection === 'business'" class="panel-card">
          <div class="panel-head">
            <div>
              <span class="products-section-kicker">Informacion del negocio</span>
              <h3>Perfil empresarial</h3>
            </div>
          </div>

          <form class="settings-form" @submit.prevent="submitSettings">
            <div class="product-form-grid">
              <div class="settings-form-section field-span-4">
                <span>Identidad fiscal y comercial</span>
              </div>

              <label class="field-group field-span-2">
                <span>Razon social</span>
                <input v-model="settings.legal_name" class="form-control" type="text" />
              </label>

              <label class="field-group field-span-2">
                <span>Nombre comercial</span>
                <input v-model="settings.trade_name" class="form-control" type="text" required />
              </label>

              <label class="field-group field-span-2">
                <span>Titulo de la app</span>
                <input v-model="settings.app_title" class="form-control" type="text" />
              </label>

              <label class="field-group field-span-2">
                <span>Subtitulo sidebar</span>
                <input v-model="settings.sidebar_subtitle" class="form-control" type="text" />
              </label>

              <label class="field-group">
                <span>RUC</span>
                <input v-model="settings.ruc" class="form-control" type="text" />
              </label>

              <div class="settings-form-section field-span-4">
                <span>Contacto visible en facturas y tickets POS</span>
              </div>

              <label class="field-group">
                <span>Telefono</span>
                <input v-model="settings.phone" class="form-control" type="text" />
              </label>

              <label class="field-group">
                <span>Telefonos</span>
                <input v-model="settings.phones" class="form-control" type="text" />
              </label>

              <label class="field-group">
                <span>Correo</span>
                <input v-model="settings.email" class="form-control" type="email" />
              </label>

              <label class="field-group field-span-2">
                <span>Direccion</span>
                <textarea v-model="settings.address" class="form-control settings-textarea"></textarea>
              </label>

              <label class="field-group field-span-2">
                <span>Pagina web</span>
                <input v-model="settings.website" class="form-control" type="text" />
              </label>

              <label class="field-group">
                <span>Tema visual</span>
                <select v-model="settings.theme_code" class="form-control">
                  <option value="default">Default</option>
                  <option value="corporate">Corporate</option>
                  <option value="odoo">Odoo</option>
                  <option value="skethy">Sketchy</option>
                </select>
              </label>

              <label class="field-group">
                <span>Moneda base costos/precios</span>
                <select v-model="settings.pricing_currency" class="form-control">
                  <option value="CS">Cordobas (C$)</option>
                  <option value="USD">Dolares (USD)</option>
                </select>
              </label>
            </div>

            <div class="panel-head">
              <div>
                <span class="products-section-kicker">Identidad visual</span>
                <h3>Branding por contexto</h3>
              </div>
            </div>

            <div class="settings-logo-grid">
              <div v-for="field in logoFields" :key="field.key" class="settings-logo-card">
                <span class="settings-logo-label">{{ field.label }}</span>
                <small v-if="field.help" class="settings-logo-help">{{ field.help }}</small>
                <div class="settings-logo-preview">
                  <img v-if="previewFor(field)" :src="previewFor(field)" :alt="field.label" />
                  <div v-else class="settings-logo-empty">
                    <i class="bi bi-image"></i>
                    <span>Sin imagen</span>
                  </div>
                </div>
                <input
                  class="form-control settings-file-input"
                  type="file"
                  accept="image/*"
                  @change="onFileChange(field.key, $event)"
                />
              </div>
            </div>

            <div class="product-form-actions">
              <Button severity="secondary" variant="outlined" type="button" @click="loadSettings">
                Recargar
              </Button>
              <Button :disabled="loading" type="submit">
                {{ loading ? "Guardando..." : "Guardar perfil empresarial" }}
              </Button>
            </div>
          </form>
        </article>

        <article v-else-if="currentSection === 'environment'" class="panel-card">
          <div class="panel-head">
            <div>
              <span class="products-section-kicker">Entorno empresarial</span>
              <h3>Multiempresa y base de datos</h3>
            </div>
          </div>

          <div class="settings-env-layout">
            <form class="settings-env-form" @submit.prevent="submitEnvironment">
              <div class="product-form-grid">
                <label class="field-group">
                  <span>Clave de empresa</span>
                  <input
                    v-model="environmentForm.company_key"
                    class="form-control"
                    type="text"
                    :disabled="Boolean(environmentForm.id)"
                    placeholder="hollywood_pacas"
                  />
                </label>

                <label class="field-group field-span-2">
                  <span>Nombre visible</span>
                  <input
                    v-model="environmentForm.company_name"
                    class="form-control"
                    type="text"
                    placeholder="Hollywood Pacas"
                  />
                </label>

                <label class="field-group field-span-2">
                  <span>DATABASE_URL</span>
                  <input
                    v-model="environmentForm.database_url"
                    class="form-control"
                    type="text"
                    placeholder="postgresql://user:1234@localhost:5432/hollpacas"
                  />
                </label>

                <label class="products-checkbox">
                  <input v-model="environmentForm.activate" type="checkbox" />
                  <span>Activar al guardar</span>
                </label>
              </div>

              <div class="product-form-actions">
                <Button type="button" severity="secondary" variant="outlined" @click="resetEnvironmentForm">
                  Limpiar
                </Button>
                <Button :disabled="environmentLoading" type="submit">
                  {{ environmentLoading ? "Guardando..." : environmentForm.id ? "Actualizar entorno" : "Registrar entorno" }}
                </Button>
              </div>
            </form>

            <div class="settings-env-list">
              <div
                v-for="environment in environments"
                :key="environment.id"
                class="settings-env-card"
                :class="{ active: environment.is_active }"
              >
                <div class="settings-env-head">
                  <div>
                    <strong>{{ environment.company_name }}</strong>
                    <span>{{ environment.company_key }}</span>
                  </div>
                  <Tag :severity="environment.is_active ? 'success' : 'contrast'" :value="environment.is_active ? 'Activo' : 'Inactivo'" />
                </div>

                <code class="settings-env-code">{{ environment.database_url }}</code>

                <div class="settings-env-actions">
                  <Button
                    type="button"
                    severity="secondary"
                    variant="outlined"
                    size="small"
                    @click="editEnvironment(environment)"
                  >
                    Editar
                  </Button>
                  <Button
                    v-if="!environment.is_active"
                    type="button"
                    size="small"
                    @click="activateEnvironment(environment.id)"
                  >
                    Activar
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </article>

        <article v-else-if="currentSection === 'exchange-rates'" class="panel-card">
          <div class="panel-head">
            <div>
              <span class="products-section-kicker">Moneda y conversiones</span>
              <h3>Tasa de cambio</h3>
              <p class="panel-text">
                Registra la tasa vigente para ventas, inventario y procesos que convierten USD/C$.
              </p>
            </div>
            <Tag
              :severity="currentExchangeRate ? 'success' : 'warn'"
              :value="currentExchangeRate ? `Vigente C$ ${formatRate(currentExchangeRate.rate)}` : 'Sin tasa vigente'"
            />
          </div>

          <div class="exchange-rate-layout">
            <form class="settings-env-form exchange-rate-form" @submit.prevent="submitExchangeRate">
              <div class="product-form-grid">
                <label class="field-group">
                  <span>Fecha efectiva</span>
                  <input v-model="exchangeRateForm.effective_date" class="form-control" type="date" required />
                </label>

                <label class="field-group">
                  <span>Periodicidad</span>
                  <select v-model="exchangeRateForm.period_type" class="form-control">
                    <option value="daily">Diaria</option>
                    <option value="monthly">Mensual</option>
                    <option value="quarterly">Trimestral</option>
                  </select>
                </label>

                <label class="field-group">
                  <span>1 USD equivale a C$</span>
                  <input
                    v-model="exchangeRateForm.rate"
                    class="form-control"
                    type="number"
                    min="0.0001"
                    step="0.0001"
                    placeholder="36.7500"
                    required
                  />
                </label>

                <label class="field-group field-span-2">
                  <span>Nota</span>
                  <input
                    v-model="exchangeRateForm.notes"
                    class="form-control"
                    placeholder="Ej. tasa oficial del dia, tasa comercial mensual..."
                  />
                </label>
              </div>

              <div class="product-form-actions">
                <Button type="button" severity="secondary" variant="outlined" @click="resetExchangeRateForm">
                  Limpiar
                </Button>
                <Button :disabled="exchangeRateLoading" type="submit">
                  {{ exchangeRateLoading ? "Guardando..." : "Registrar tasa" }}
                </Button>
              </div>
            </form>

            <div class="exchange-rate-list">
              <div v-if="!exchangeRates.length" class="empty-state">No hay tasas registradas.</div>
              <template v-else>
                <article
                  v-for="rate in exchangeRates"
                  :key="rate.id"
                  class="exchange-rate-card"
                  :class="{ active: currentExchangeRate?.id === rate.id }"
                >
                  <div>
                    <strong>C$ {{ formatRate(rate.rate) }}</strong>
                    <span>{{ formatPeriod(rate.period_type) }} desde {{ rate.effective_date }}</span>
                    <small v-if="rate.notes">{{ rate.notes }}</small>
                  </div>
                  <Tag :severity="currentExchangeRate?.id === rate.id ? 'success' : 'contrast'" :value="currentExchangeRate?.id === rate.id ? 'Vigente' : 'Historial'" />
                </article>
              </template>
            </div>
          </div>
        </article>

        <article v-else-if="currentSection === 'third-parties'" class="panel-card">
          <div class="panel-head">
            <div>
              <span class="products-section-kicker">Catalogos comerciales</span>
              <h3>Clientes, vendedores y proveedores</h3>
              <p class="panel-text">
                Administra los terceros usados por ventas, compras e inventario desde una sola configuracion.
              </p>
            </div>
            <Tag severity="info" :value="`${customers.length + vendors.length + providers.length} registros`" />
          </div>

          <div class="third-party-tabs">
            <button
              v-for="tab in thirdPartyTabs"
              :key="tab.key"
              type="button"
              :class="{ active: activeThirdPartyTab === tab.key }"
              @click="activeThirdPartyTab = tab.key"
            >
              <i class="bi" :class="tab.icon"></i>
              <span>{{ tab.label }}</span>
            </button>
          </div>

          <div v-if="activeThirdPartyTab === 'customers'" class="third-party-layout">
            <form class="settings-env-form" @submit.prevent="submitCustomer">
              <div class="product-form-grid">
                <label class="field-group field-span-2">
                  <span>Nombre del cliente</span>
                  <input v-model.trim="customerForm.nombre" class="form-control" placeholder="Cliente general o empresa" required />
                </label>
                <label class="field-group">
                  <span>RUC / Cedula</span>
                  <input v-model.trim="customerForm.identificacion" class="form-control" />
                </label>
                <label class="field-group">
                  <span>Telefono</span>
                  <input v-model.trim="customerForm.telefono" class="form-control" />
                </label>
                <label class="field-group">
                  <span>Correo</span>
                  <input v-model.trim="customerForm.email" class="form-control" type="email" />
                </label>
                <label class="field-group">
                  <span>Tipo</span>
                  <input v-model.trim="customerForm.tipo" class="form-control" placeholder="Retail, mayorista..." />
                </label>
                <label class="field-group field-span-2">
                  <span>Direccion</span>
                  <input v-model.trim="customerForm.direccion" class="form-control" />
                </label>
                <label class="products-checkbox">
                  <input v-model="customerForm.activo" type="checkbox" />
                  <span>Activo</span>
                </label>
              </div>
              <div class="product-form-actions">
                <Button type="button" severity="secondary" variant="outlined" @click="resetCustomerForm">Limpiar</Button>
                <Button :disabled="thirdPartyLoading" type="submit">{{ customerForm.id ? "Actualizar cliente" : "Crear cliente" }}</Button>
              </div>
            </form>

            <div class="third-party-list">
              <article v-for="customer in customers" :key="customer.id" class="third-party-card">
                <div>
                  <strong>{{ customer.nombre }}</strong>
                  <span>{{ customer.identificacion || customer.telefono || "Sin documento" }}</span>
                </div>
                <div class="third-party-actions">
                  <Tag :severity="customer.activo ? 'success' : 'contrast'" :value="customer.activo ? 'Activo' : 'Inactivo'" />
                  <Button size="small" severity="secondary" variant="outlined" label="Editar" @click="editCustomer(customer)" />
                </div>
              </article>
              <div v-if="!customers.length" class="empty-state">No hay clientes registrados.</div>
            </div>
          </div>

          <div v-else-if="activeThirdPartyTab === 'vendors'" class="third-party-layout">
            <form class="settings-env-form" @submit.prevent="submitVendor">
              <div class="product-form-grid">
                <label class="field-group">
                  <span>Codigo</span>
                  <input v-model.trim="vendorForm.code" class="form-control" placeholder="VEN-PISO" required />
                </label>
                <label class="field-group field-span-2">
                  <span>Nombre del vendedor</span>
                  <input v-model.trim="vendorForm.nombre" class="form-control" placeholder="Vendedor de piso" required />
                </label>
                <label class="field-group">
                  <span>Usuario vinculado</span>
                  <select v-model="vendorForm.user_id" class="form-control">
                    <option :value="null">Sin usuario</option>
                    <option v-for="user in users" :key="user.id" :value="user.id">{{ user.full_name || user.email }}</option>
                  </select>
                </label>
                <label class="field-group">
                  <span>Sucursal</span>
                  <select v-model="vendorForm.sucursal_id" class="form-control">
                    <option :value="null">Sin sucursal</option>
                    <option v-for="branch in branches" :key="branch.id" :value="branch.id">{{ branch.name }}</option>
                  </select>
                </label>
                <label class="field-group">
                  <span>Bodega</span>
                  <select v-model="vendorForm.bodega_id" class="form-control">
                    <option :value="null">Sin bodega fija</option>
                    <option v-for="bodega in bodegas" :key="bodega.id" :value="bodega.id">{{ bodega.name }}</option>
                  </select>
                </label>
                <label class="field-group">
                  <span>Telefono</span>
                  <input v-model.trim="vendorForm.telefono" class="form-control" />
                </label>
                <label class="field-group">
                  <span>Correo</span>
                  <input v-model.trim="vendorForm.email" class="form-control" type="email" />
                </label>
                <label class="products-checkbox">
                  <input v-model="vendorForm.activo" type="checkbox" />
                  <span>Activo</span>
                </label>
              </div>
              <div class="product-form-actions">
                <Button type="button" severity="secondary" variant="outlined" @click="resetVendorForm">Limpiar</Button>
                <Button :disabled="thirdPartyLoading" type="submit">{{ vendorForm.id ? "Actualizar vendedor" : "Crear vendedor" }}</Button>
              </div>
            </form>

            <div class="third-party-list">
              <article v-for="vendor in vendors" :key="vendor.id" class="third-party-card">
                <div>
                  <strong>{{ vendor.nombre }}</strong>
                  <span>{{ vendor.code }} · {{ vendor.bodega_name || "Sin bodega fija" }}</span>
                </div>
                <div class="third-party-actions">
                  <Tag :severity="vendor.activo ? 'success' : 'contrast'" :value="vendor.activo ? 'Activo' : 'Inactivo'" />
                  <Button size="small" severity="secondary" variant="outlined" label="Editar" @click="editVendor(vendor)" />
                </div>
              </article>
              <div v-if="!vendors.length" class="empty-state">No hay vendedores registrados.</div>
            </div>
          </div>

          <div v-else class="third-party-layout">
            <form class="settings-env-form" @submit.prevent="submitProvider">
              <div class="product-form-grid">
                <label class="field-group field-span-2">
                  <span>Nombre del proveedor</span>
                  <input v-model.trim="providerForm.nombre" class="form-control" placeholder="Proveedor local" required />
                </label>
                <label class="field-group">
                  <span>Tipo</span>
                  <input v-model.trim="providerForm.tipo" class="form-control" placeholder="Local, internacional..." />
                </label>
                <label class="products-checkbox">
                  <input v-model="providerForm.activo" type="checkbox" />
                  <span>Activo</span>
                </label>
              </div>
              <div class="product-form-actions">
                <Button type="button" severity="secondary" variant="outlined" @click="resetProviderForm">Limpiar</Button>
                <Button :disabled="thirdPartyLoading" type="submit">{{ providerForm.id ? "Actualizar proveedor" : "Crear proveedor" }}</Button>
              </div>
            </form>

            <div class="third-party-list">
              <article v-for="provider in providers" :key="provider.id" class="third-party-card">
                <div>
                  <strong>{{ provider.nombre }}</strong>
                  <span>{{ provider.tipo || "Proveedor" }}</span>
                </div>
                <div class="third-party-actions">
                  <Tag :severity="provider.activo ? 'success' : 'contrast'" :value="provider.activo ? 'Activo' : 'Inactivo'" />
                  <Button size="small" severity="secondary" variant="outlined" label="Editar" @click="editProvider(provider)" />
                </div>
              </article>
              <div v-if="!providers.length" class="empty-state">No hay proveedores registrados.</div>
            </div>
          </div>
        </article>

        <article v-else-if="currentSection === 'catalogs'" class="panel-card">
          <div class="panel-head">
            <div>
              <span class="products-section-kicker">Catalogos de productos</span>
              <h3>Lineas y marcas</h3>
              <p class="panel-text">
                Crea y mantiene los catalogos que se usan al registrar productos.
              </p>
            </div>
            <Tag severity="info" :value="`${lineas.length + marcas.length} registros`" />
          </div>

          <div class="third-party-tabs">
            <button
              v-for="tab in productCatalogTabs"
              :key="tab.key"
              type="button"
              :class="{ active: activeCatalogTab === tab.key }"
              @click="activeCatalogTab = tab.key"
            >
              <i class="bi" :class="tab.icon"></i>
              <span>{{ tab.label }}</span>
            </button>
          </div>

          <div v-if="activeCatalogTab === 'lineas'" class="third-party-layout">
            <form class="settings-env-form" @submit.prevent="submitLinea">
              <div class="product-form-grid">
                <label class="field-group">
                  <span>Codigo de linea</span>
                  <input
                    v-model.trim="lineaForm.cod_linea"
                    class="form-control"
                    type="text"
                    maxlength="50"
                    placeholder="ROPA"
                    required
                    @input="lineaForm.cod_linea = toUpperValue(lineaForm.cod_linea)"
                  />
                </label>
                <label class="field-group field-span-2">
                  <span>Nombre de linea</span>
                  <input
                    v-model.trim="lineaForm.linea"
                    class="form-control"
                    type="text"
                    maxlength="120"
                    placeholder="ROPA AMERICANA"
                    required
                    @input="lineaForm.linea = toUpperValue(lineaForm.linea)"
                  />
                </label>
                <label class="products-checkbox">
                  <input v-model="lineaForm.activo" type="checkbox" />
                  <span>Activa</span>
                </label>
              </div>
              <div class="product-form-actions">
                <Button type="button" severity="secondary" variant="outlined" @click="resetLineaForm">Limpiar</Button>
                <Button :disabled="catalogLoading" type="submit">
                  {{ lineaForm.id ? "Actualizar linea" : "Crear linea" }}
                </Button>
              </div>
            </form>

            <div class="third-party-list">
              <article v-for="linea in lineas" :key="linea.id" class="third-party-card">
                <div>
                  <strong>{{ linea.linea }}</strong>
                  <span>{{ linea.cod_linea || "Sin codigo" }}</span>
                </div>
                <div class="third-party-actions">
                  <Tag :severity="linea.activo ? 'success' : 'contrast'" :value="linea.activo ? 'Activa' : 'Inactiva'" />
                  <Button size="small" severity="secondary" variant="outlined" label="Editar" @click="editLinea(linea)" />
                </div>
              </article>
              <div v-if="!lineas.length" class="empty-state">No hay lineas registradas.</div>
            </div>
          </div>

          <div v-else class="third-party-layout">
            <form class="settings-env-form" @submit.prevent="submitMarca">
              <div class="product-form-grid">
                <label class="field-group field-span-2">
                  <span>Nombre de marca</span>
                  <input
                    v-model.trim="marcaForm.nombre"
                    class="form-control"
                    type="text"
                    maxlength="120"
                    placeholder="SIN MARCA"
                    required
                    @input="marcaForm.nombre = toUpperValue(marcaForm.nombre)"
                  />
                </label>
                <label class="products-checkbox">
                  <input v-model="marcaForm.activo" type="checkbox" />
                  <span>Activa</span>
                </label>
              </div>
              <div class="product-form-actions">
                <Button type="button" severity="secondary" variant="outlined" @click="resetMarcaForm">Limpiar</Button>
                <Button :disabled="catalogLoading" type="submit">
                  {{ marcaForm.id ? "Actualizar marca" : "Crear marca" }}
                </Button>
              </div>
            </form>

            <div class="third-party-list">
              <article v-for="marca in marcas" :key="marca.id" class="third-party-card">
                <div>
                  <strong>{{ marca.nombre }}</strong>
                  <span>Catalogo de marcas</span>
                </div>
                <div class="third-party-actions">
                  <Tag :severity="marca.activo ? 'success' : 'contrast'" :value="marca.activo ? 'Activa' : 'Inactiva'" />
                  <Button size="small" severity="secondary" variant="outlined" label="Editar" @click="editMarca(marca)" />
                </div>
              </article>
              <div v-if="!marcas.length" class="empty-state">No hay marcas registradas.</div>
            </div>
          </div>
        </article>

        <article v-else-if="currentSection === 'policies'" class="panel-card">
          <div class="panel-head">
            <div>
              <span class="products-section-kicker">Politicas del negocio</span>
              <h3>Reglas operativas del entorno</h3>
            </div>
          </div>

          <form class="settings-form" @submit.prevent="submitSettings">
            <div class="settings-policy-grid">
              <label v-for="policy in policyFields" :key="policy.key" class="settings-policy-card">
                <div class="settings-policy-copy">
                  <strong>{{ policy.label }}</strong>
                  <span>{{ policy.help }}</span>
                </div>
                <input v-model="settings[policy.key]" type="checkbox" />
              </label>

              <label class="field-group">
                <span>Moneda base de costos y precios</span>
                <select v-model="settings.pricing_currency" class="form-control">
                  <option value="CS">Cordobas (C$)</option>
                  <option value="USD">Dolares (USD)</option>
                </select>
              </label>

              <label class="field-group">
                <span>Porcentaje de ganancia (%)</span>
                <input
                  v-model.number="settings.price_margin_percent"
                  class="form-control"
                  type="number"
                  min="0"
                  step="1"
                />
              </label>
            </div>

            <div class="product-form-actions">
              <Button :disabled="loading" type="submit">
                {{ loading ? "Guardando..." : "Guardar politicas" }}
              </Button>
            </div>
          </form>
        </article>

        <article v-else class="panel-card">
          <div class="panel-head">
            <div>
              <span class="products-section-kicker">Interfaz de ventas</span>
              <h3>Arquitectura activa del POS</h3>
            </div>
          </div>

          <form class="settings-form" @submit.prevent="submitSettings">
            <div class="product-form-grid">
              <label class="field-group field-span-2">
                <span>Tipo de interfaz</span>
                <select v-model="settings.sales_interface_code" class="form-control">
                  <option
                    v-for="option in salesInterfaceOptions"
                    :key="option.code"
                    :value="option.code"
                  >
                    {{ option.label }}
                  </option>
                </select>
              </label>
            </div>

            <div class="settings-env-list">
              <div
                v-for="option in salesInterfaceOptions"
                :key="option.code"
                class="settings-env-card"
                :class="{ active: settings.sales_interface_code === option.code }"
              >
                <div class="settings-env-head">
                  <div>
                    <strong>{{ option.label }}</strong>
                    <span>{{ option.description }}</span>
                  </div>
                  <Tag
                    :severity="settings.sales_interface_code === option.code ? 'success' : 'contrast'"
                    :value="settings.sales_interface_code === option.code ? 'Activa' : 'Disponible'"
                  />
                </div>
              </div>
            </div>

            <div class="product-form-actions">
              <Button :disabled="loading" type="submit">
                {{ loading ? "Guardando..." : "Guardar interfaz de ventas" }}
              </Button>
            </div>
          </form>
        </article>

      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import Button from "primevue/button";
import Tag from "primevue/tag";

import { createVendor, fetchAccessUsers, fetchBranches, fetchVendors, updateVendor } from "../../services/access";
import {
  createLinea,
  createMarca,
  createProveedor,
  fetchInventoryCatalogs,
  updateLinea,
  updateMarca,
  updateProveedor,
} from "../../services/inventory";
import { createCustomer, fetchCustomers, updateCustomer } from "../../services/sales";
import {
  activateCompanyEnvironment,
  buildAssetUrl,
  createExchangeRate,
  createCompanyEnvironment,
  fetchBusinessSettings,
  fetchCompanyEnvironments,
  fetchCurrentExchangeRate,
  fetchExchangeRates,
  saveBusinessSettings,
  updateCompanyEnvironment,
} from "../../services/settings";

const sections = [
  {
    key: "business",
    label: "Informacion del negocio",
    caption: "Perfil, branding y datos corporativos",
    icon: "bi-building",
  },
  {
    key: "catalogs",
    label: "Catalogos",
    caption: "Lineas y marcas de productos",
    icon: "bi-tags",
  },
  {
    key: "environment",
    label: "Entorno empresarial",
    caption: "Multiempresa y base de datos activa",
    icon: "bi-buildings",
  },
  {
    key: "exchange-rates",
    label: "Tasa de cambio",
    caption: "Registro diario, mensual o trimestral",
    icon: "bi-currency-exchange",
  },
  {
    key: "third-parties",
    label: "Terceros",
    caption: "Clientes, vendedores y proveedores",
    icon: "bi-person-lines-fill",
  },
  {
    key: "policies",
    label: "Politicas del negocio",
    caption: "Reglas de inventario, ventas y costos",
    icon: "bi-sliders",
  },
  {
    key: "sales-interface",
    label: "Interfaz de ventas",
    caption: "Arquitectura operativa del punto de venta",
    icon: "bi-window-stack",
  },
];

const thirdPartyTabs = [
  { key: "customers", label: "Clientes", icon: "bi-people" },
  { key: "vendors", label: "Vendedores", icon: "bi-person-badge" },
  { key: "providers", label: "Proveedores", icon: "bi-truck" },
];

const productCatalogTabs = [
  { key: "lineas", label: "Lineas", icon: "bi-diagram-3" },
  { key: "marcas", label: "Marcas", icon: "bi-tags" },
];

const salesInterfaceOptions = [
  {
    code: "ecommerce",
    label: "Vista ecommerce elegante",
    description: "Lista limpia para comercios de catalogo, ropa, pacas y venta asistida.",
  },
  {
    code: "supermarket",
    label: "Vista supermercado en grilla",
    description: "Tarjetas rapidas para tocar, cargar productos y facturar en mostrador.",
  },
  {
    code: "hardware",
    label: "Vista ferreteria / busqueda general",
    description: "Filas densas por codigo, barra, stock y precio para busqueda tecnica.",
  },
];

const logoFields = [
  { key: "logo_login", label: "Logo de login" },
  {
    key: "logo_sidebar",
    label: "Logo del comercio",
    help: "Se muestra en el menu lateral y tambien se usa como favicon del navegador.",
  },
  { key: "logo_invoice", label: "Logo de factura" },
];

const policyFields = [
  { key: "inventory_cs_only", label: "Inventario en Cordobas (C$)", help: "Operacion de inventario usa Cordobas como moneda principal del entorno." },
  { key: "weighted_inventory_enabled", label: "Ingresos por peso", help: "Habilita libras, kilos y onzas en catalogo e ingresos." },
  { key: "weighted_sales_enabled", label: "Ventas por peso", help: "Facturacion solicita el peso exacto antes de vender." },
  { key: "recipe_explosion_on_ingreso", label: "Explosion de recetas pre ingreso", help: "Descarga materias primas automaticamente al ingresar produccion." },
  { key: "multi_branch_enabled", label: "Multi sucursales", help: "Activa sucursales y bodegas por entorno empresarial." },
  { key: "price_auto_from_cost_enabled", label: "Auto calcular precio desde costo", help: "Calcula Precio 1 a partir del costo y el margen configurado." },
];

const currentSection = ref("business");
const loading = ref(false);
const environmentLoading = ref(false);
const exchangeRateLoading = ref(false);
const thirdPartyLoading = ref(false);
const catalogLoading = ref(false);
const error = ref("");
const success = ref("");
const environments = ref([]);
const exchangeRates = ref([]);
const currentExchangeRate = ref(null);
const activeThirdPartyTab = ref("customers");
const customers = ref([]);
const vendors = ref([]);
const providers = ref([]);
const lineas = ref([]);
const marcas = ref([]);
const users = ref([]);
const branches = ref([]);
const bodegas = ref([]);
const activeCatalogTab = ref("lineas");
const files = reactive({
  logo_login: null,
  logo_sidebar: null,
  logo_invoice: null,
});
const previews = reactive({
  logo_login: "",
  logo_sidebar: "",
  logo_invoice: "",
});
const settings = reactive({
  business_name: "",
  legal_name: "",
  trade_name: "",
  app_title: "",
  sidebar_subtitle: "",
  address: "",
  ruc: "",
  phone: "",
  phones: "",
  email: "",
  website: "",
  theme_code: "default",
  sales_interface_code: "ecommerce",
  pricing_currency: "CS",
  logo_login: "",
  logo_sidebar: "",
  logo_invoice: "",
  logo_favicon: "",
  inventory_cs_only: false,
  weighted_inventory_enabled: false,
  weighted_sales_enabled: false,
  recipe_explosion_on_ingreso: false,
  multi_branch_enabled: false,
  price_auto_from_cost_enabled: false,
  price_margin_percent: 0,
});
const environmentForm = reactive({
  id: null,
  company_key: "",
  company_name: "",
  database_url: "",
  activate: false,
});
const exchangeRateForm = reactive({
  effective_date: new Date().toISOString().slice(0, 10),
  period_type: "daily",
  rate: "",
  notes: "",
});
const customerForm = reactive(getEmptyCustomerForm());
const vendorForm = reactive(getEmptyVendorForm());
const providerForm = reactive(getEmptyProviderForm());
const lineaForm = reactive(getEmptyLineaForm());
const marcaForm = reactive(getEmptyMarcaForm());

const enabledPolicies = computed(
  () =>
    policyFields.reduce((total, policy) => total + (settings[policy.key] ? 1 : 0), 0),
);

function applySettings(payload) {
  settings.business_name = payload.business_name || "";
  settings.legal_name = payload.legal_name || "";
  settings.trade_name = payload.trade_name || payload.business_name || "";
  settings.app_title = payload.app_title || "";
  settings.sidebar_subtitle = payload.sidebar_subtitle || "";
  settings.address = payload.address || "";
  settings.ruc = payload.ruc || "";
  settings.phone = payload.phone || "";
  settings.phones = payload.phones || "";
  settings.email = payload.email || "";
  settings.website = payload.website || "";
  settings.theme_code = payload.theme_code || "default";
  settings.sales_interface_code = payload.sales_interface_code || "ecommerce";
  settings.pricing_currency = payload.pricing_currency || "CS";
  settings.logo_login = payload.logo_login || "";
  settings.logo_sidebar = payload.logo_sidebar || "";
  settings.logo_invoice = payload.logo_invoice || "";
  settings.logo_favicon = payload.logo_favicon || "";
  settings.inventory_cs_only = Boolean(payload.inventory_cs_only);
  settings.weighted_inventory_enabled = Boolean(payload.weighted_inventory_enabled);
  settings.weighted_sales_enabled = Boolean(payload.weighted_sales_enabled);
  settings.recipe_explosion_on_ingreso = Boolean(payload.recipe_explosion_on_ingreso);
  settings.multi_branch_enabled = Boolean(payload.multi_branch_enabled);
  settings.price_auto_from_cost_enabled = Boolean(payload.price_auto_from_cost_enabled);
  settings.price_margin_percent = Number(payload.price_margin_percent || 0);
  environments.value = Array.isArray(payload.environments) ? payload.environments : [];
}

function previewFor(field) {
  return previews[field.key] || buildAssetUrl(settings[field.key]);
}

function onFileChange(key, event) {
  const [file] = event.target.files || [];
  files[key] = file || null;
  previews[key] = file ? URL.createObjectURL(file) : "";
}

function resetEnvironmentForm() {
  environmentForm.id = null;
  environmentForm.company_key = "";
  environmentForm.company_name = "";
  environmentForm.database_url = "";
  environmentForm.activate = false;
}

function editEnvironment(environment) {
  environmentForm.id = environment.id;
  environmentForm.company_key = environment.company_key;
  environmentForm.company_name = environment.company_name;
  environmentForm.database_url = environment.database_url;
  environmentForm.activate = Boolean(environment.is_active);
  currentSection.value = "environment";
}

function resetExchangeRateForm() {
  exchangeRateForm.effective_date = new Date().toISOString().slice(0, 10);
  exchangeRateForm.period_type = "daily";
  exchangeRateForm.rate = "";
  exchangeRateForm.notes = "";
}

function formatRate(value) {
  return new Intl.NumberFormat("es-NI", {
    minimumFractionDigits: 4,
    maximumFractionDigits: 4,
  }).format(Number(value || 0));
}

function formatPeriod(value) {
  const labels = {
    daily: "Diaria",
    monthly: "Mensual",
    quarterly: "Trimestral",
  };
  return labels[value] || "Diaria";
}

function getEmptyCustomerForm() {
  return { id: null, nombre: "", telefono: "", identificacion: "", direccion: "", email: "", tipo: "", activo: true };
}

function getEmptyVendorForm() {
  return {
    id: null,
    code: "",
    nombre: "Vendedor de piso",
    user_id: null,
    sucursal_id: null,
    bodega_id: null,
    telefono: "",
    email: "",
    meta_ventas: null,
    activo: true,
  };
}

function getEmptyProviderForm() {
  return { id: null, nombre: "", tipo: "", activo: true };
}

function getEmptyLineaForm() {
  return { id: null, cod_linea: "", linea: "", activo: true };
}

function getEmptyMarcaForm() {
  return { id: null, nombre: "", activo: true };
}

function toUpperValue(value) {
  return (value || "").toString().toUpperCase();
}

function nextVendorCode() {
  if (!vendors.value.length) return "VEN-PISO";
  return `VEN-${String(vendors.value.length + 1).padStart(3, "0")}`;
}

function normalizeNullableId(value) {
  if (value === "" || value === undefined || value === null) return null;
  const numericValue = Number(value);
  return Number.isFinite(numericValue) ? numericValue : null;
}

function resetCustomerForm() {
  Object.assign(customerForm, getEmptyCustomerForm());
}

function resetVendorForm() {
  Object.assign(vendorForm, getEmptyVendorForm(), { code: nextVendorCode() });
}

function resetProviderForm() {
  Object.assign(providerForm, getEmptyProviderForm());
}

function resetLineaForm() {
  Object.assign(lineaForm, getEmptyLineaForm());
}

function resetMarcaForm() {
  Object.assign(marcaForm, getEmptyMarcaForm());
}

function editCustomer(customer) {
  Object.assign(customerForm, getEmptyCustomerForm(), customer);
  activeThirdPartyTab.value = "customers";
}

function editVendor(vendor) {
  Object.assign(vendorForm, getEmptyVendorForm(), {
    ...vendor,
    user_id: vendor.user_id ?? null,
    sucursal_id: vendor.sucursal_id ?? null,
    bodega_id: vendor.bodega_id ?? null,
  });
  activeThirdPartyTab.value = "vendors";
}

function editProvider(provider) {
  Object.assign(providerForm, getEmptyProviderForm(), provider);
  activeThirdPartyTab.value = "providers";
}

function editLinea(linea) {
  Object.assign(lineaForm, getEmptyLineaForm(), {
    id: linea.id,
    cod_linea: linea.cod_linea || "",
    linea: linea.linea || "",
    activo: Boolean(linea.activo),
  });
  activeCatalogTab.value = "lineas";
}

function editMarca(marca) {
  Object.assign(marcaForm, getEmptyMarcaForm(), {
    id: marca.id,
    nombre: marca.nombre || "",
    activo: Boolean(marca.activo),
  });
  activeCatalogTab.value = "marcas";
}

async function loadThirdParties() {
  try {
    const [customerData, vendorData, userData, branchData, catalogData] = await Promise.all([
      fetchCustomers("", true),
      fetchVendors(),
      fetchAccessUsers(),
      fetchBranches(),
      fetchInventoryCatalogs(),
    ]);
    customers.value = Array.isArray(customerData) ? customerData : [];
    vendors.value = Array.isArray(vendorData) ? vendorData : [];
    users.value = Array.isArray(userData) ? userData : [];
    branches.value = Array.isArray(branchData) ? branchData : [];
    providers.value = Array.isArray(catalogData?.proveedores) ? catalogData.proveedores : [];
    bodegas.value = Array.isArray(catalogData?.bodegas) ? catalogData.bodegas : [];
    lineas.value = Array.isArray(catalogData?.lineas) ? catalogData.lineas : [];
    marcas.value = Array.isArray(catalogData?.marcas) ? catalogData.marcas : [];
    if (!vendorForm.id && !vendorForm.code) {
      resetVendorForm();
    }
  } catch (err) {
    error.value = err.message || "No se pudieron cargar los catalogos de terceros";
  }
}

async function loadProductCatalogs() {
  try {
    const catalogData = await fetchInventoryCatalogs();
    lineas.value = Array.isArray(catalogData?.lineas) ? catalogData.lineas : [];
    marcas.value = Array.isArray(catalogData?.marcas) ? catalogData.marcas : [];
  } catch (err) {
    error.value = err.message || "No se pudieron cargar las lineas y marcas";
  }
}

async function submitLinea() {
  catalogLoading.value = true;
  error.value = "";
  success.value = "";
  try {
    const payload = {
      cod_linea: lineaForm.cod_linea,
      linea: lineaForm.linea,
      activo: Boolean(lineaForm.activo),
    };
    if (lineaForm.id) {
      await updateLinea(lineaForm.id, payload);
      success.value = "Linea actualizada.";
    } else {
      await createLinea(payload);
      success.value = "Linea creada.";
    }
    await loadProductCatalogs();
    resetLineaForm();
  } catch (err) {
    error.value = err.message || "No se pudo guardar la linea";
  } finally {
    catalogLoading.value = false;
  }
}

async function submitMarca() {
  catalogLoading.value = true;
  error.value = "";
  success.value = "";
  try {
    const payload = {
      nombre: marcaForm.nombre,
      activo: Boolean(marcaForm.activo),
    };
    if (marcaForm.id) {
      await updateMarca(marcaForm.id, payload);
      success.value = "Marca actualizada.";
    } else {
      await createMarca(payload);
      success.value = "Marca creada.";
    }
    await loadProductCatalogs();
    resetMarcaForm();
  } catch (err) {
    error.value = err.message || "No se pudo guardar la marca";
  } finally {
    catalogLoading.value = false;
  }
}

async function submitCustomer() {
  thirdPartyLoading.value = true;
  error.value = "";
  success.value = "";
  try {
    const payload = {
      nombre: customerForm.nombre,
      telefono: customerForm.telefono,
      identificacion: customerForm.identificacion,
      direccion: customerForm.direccion,
      email: customerForm.email,
      tipo: customerForm.tipo,
      activo: Boolean(customerForm.activo),
    };
    if (customerForm.id) {
      await updateCustomer(customerForm.id, payload);
      success.value = "Cliente actualizado.";
    } else {
      await createCustomer(payload);
      success.value = "Cliente creado.";
    }
    await loadThirdParties();
    resetCustomerForm();
  } catch (err) {
    error.value = err.message || "No se pudo guardar el cliente";
  } finally {
    thirdPartyLoading.value = false;
  }
}

async function submitVendor() {
  thirdPartyLoading.value = true;
  error.value = "";
  success.value = "";
  try {
    const payload = {
      code: vendorForm.code,
      nombre: vendorForm.nombre,
      user_id: normalizeNullableId(vendorForm.user_id),
      sucursal_id: normalizeNullableId(vendorForm.sucursal_id),
      bodega_id: normalizeNullableId(vendorForm.bodega_id),
      telefono: vendorForm.telefono,
      email: vendorForm.email,
      meta_ventas: vendorForm.meta_ventas,
      activo: Boolean(vendorForm.activo),
    };
    if (vendorForm.id) {
      await updateVendor(vendorForm.id, payload);
      success.value = "Vendedor actualizado.";
    } else {
      await createVendor(payload);
      success.value = "Vendedor creado.";
    }
    await loadThirdParties();
    resetVendorForm();
  } catch (err) {
    error.value = err.message || "No se pudo guardar el vendedor";
  } finally {
    thirdPartyLoading.value = false;
  }
}

async function submitProvider() {
  thirdPartyLoading.value = true;
  error.value = "";
  success.value = "";
  try {
    const payload = {
      nombre: providerForm.nombre,
      tipo: providerForm.tipo,
      activo: Boolean(providerForm.activo),
    };
    if (providerForm.id) {
      await updateProveedor(providerForm.id, payload);
      success.value = "Proveedor actualizado.";
    } else {
      await createProveedor(payload);
      success.value = "Proveedor creado.";
    }
    await loadThirdParties();
    resetProviderForm();
  } catch (err) {
    error.value = err.message || "No se pudo guardar el proveedor";
  } finally {
    thirdPartyLoading.value = false;
  }
}

async function loadSettings() {
  error.value = "";
  success.value = "";

  try {
    const payload = await fetchBusinessSettings();
    applySettings(payload);
  } catch (err) {
    error.value = err.message || "No se pudo cargar la configuracion";
  }
}

async function loadEnvironments() {
  try {
    environments.value = await fetchCompanyEnvironments();
  } catch (err) {
    error.value = err.message || "No se pudieron cargar los entornos";
  }
}

async function loadExchangeRates() {
  try {
    const [currentRate, rates] = await Promise.all([
      fetchCurrentExchangeRate(),
      fetchExchangeRates(),
    ]);
    currentExchangeRate.value = currentRate || null;
    exchangeRates.value = Array.isArray(rates) ? rates : [];
  } catch (err) {
    error.value = err.message || "No se pudieron cargar las tasas de cambio";
  }
}

async function submitSettings() {
  loading.value = true;
  error.value = "";
  success.value = "";

  try {
    const formData = new FormData();
    formData.append("business_name", settings.trade_name || settings.business_name || "");
    formData.append("legal_name", settings.legal_name || "");
    formData.append("trade_name", settings.trade_name || "");
    formData.append("app_title", settings.app_title || "");
    formData.append("sidebar_subtitle", settings.sidebar_subtitle || "");
    formData.append("address", settings.address || "");
    formData.append("ruc", settings.ruc || "");
    formData.append("phone", settings.phone || "");
    formData.append("phones", settings.phones || "");
    formData.append("email", settings.email || "");
    formData.append("website", settings.website || "");
    formData.append("theme_code", settings.theme_code || "default");
    formData.append("sales_interface_code", settings.sales_interface_code || "ecommerce");
    formData.append("pricing_currency", settings.pricing_currency || "CS");
    formData.append("inventory_cs_only", String(Boolean(settings.inventory_cs_only)));
    formData.append("weighted_inventory_enabled", String(Boolean(settings.weighted_inventory_enabled)));
    formData.append("weighted_sales_enabled", String(Boolean(settings.weighted_sales_enabled)));
    formData.append("recipe_explosion_on_ingreso", String(Boolean(settings.recipe_explosion_on_ingreso)));
    formData.append("multi_branch_enabled", String(Boolean(settings.multi_branch_enabled)));
    formData.append("price_auto_from_cost_enabled", String(Boolean(settings.price_auto_from_cost_enabled)));
    formData.append("price_margin_percent", String(Number(settings.price_margin_percent || 0)));

    Object.entries(files).forEach(([key, file]) => {
      if (file) {
        formData.append(key, file);
      }
    });

    await saveBusinessSettings(formData);
    const persisted = await fetchBusinessSettings();
    applySettings(persisted);
    Object.keys(files).forEach((key) => {
      files[key] = null;
      previews[key] = "";
    });
    success.value =
      currentSection.value === "policies"
        ? "Politicas del negocio actualizadas."
        : "Configuracion empresarial actualizada.";
    setTimeout(() => {
      if (success.value) {
        success.value = "";
      }
    }, 3500);
  } catch (err) {
    error.value = err.message || "No se pudo guardar la configuracion";
  } finally {
    loading.value = false;
  }
}

async function submitEnvironment() {
  environmentLoading.value = true;
  error.value = "";
  success.value = "";

  try {
    const formData = new FormData();
    formData.append("company_key", environmentForm.company_key || "");
    formData.append("company_name", environmentForm.company_name || "");
    formData.append("database_url", environmentForm.database_url || "");
    formData.append("activate", String(Boolean(environmentForm.activate)));

    if (environmentForm.id) {
      await updateCompanyEnvironment(environmentForm.id, formData);
      success.value = "Entorno empresarial actualizado.";
    } else {
      await createCompanyEnvironment(formData);
      success.value = "Entorno empresarial registrado.";
    }
    setTimeout(() => {
      if (success.value) {
        success.value = "";
      }
    }, 3500);
    await loadEnvironments();
    resetEnvironmentForm();
  } catch (err) {
    error.value = err.message || "No se pudo guardar el entorno";
  } finally {
    environmentLoading.value = false;
  }
}

async function activateEnvironment(environmentId) {
  error.value = "";
  success.value = "";
  try {
    await activateCompanyEnvironment(environmentId);
    await loadEnvironments();
    success.value = "Entorno activo actualizado.";
    setTimeout(() => {
      if (success.value) {
        success.value = "";
      }
    }, 3500);
  } catch (err) {
    error.value = err.message || "No se pudo activar el entorno";
  }
}

async function submitExchangeRate() {
  exchangeRateLoading.value = true;
  error.value = "";
  success.value = "";

  try {
    const formData = new FormData();
    formData.append("effective_date", exchangeRateForm.effective_date || "");
    formData.append("period_type", exchangeRateForm.period_type || "daily");
    formData.append("rate", String(exchangeRateForm.rate || ""));
    formData.append("notes", exchangeRateForm.notes || "");
    formData.append("is_active", "true");

    await createExchangeRate(formData);
    await loadExchangeRates();
    resetExchangeRateForm();
    success.value = "Tasa de cambio registrada y disponible para conversiones.";
    setTimeout(() => {
      if (success.value) {
        success.value = "";
      }
    }, 3500);
  } catch (err) {
    error.value = err.message || "No se pudo registrar la tasa de cambio";
  } finally {
    exchangeRateLoading.value = false;
  }
}

onMounted(async () => {
  await loadSettings();
  await loadEnvironments();
  await loadExchangeRates();
  await loadThirdParties();
});
</script>
