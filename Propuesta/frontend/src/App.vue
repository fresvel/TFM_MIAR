<template>
  <div class="app-shell">
    <SidebarNav
      :coverage-tone="coverageTone"
      :current-section="currentSection"
      :has-result="Boolean(result)"
      :result="result"
      :risk-tone="riskTone"
      :sections="sections"
      @open-viewer="openViewer"
    />
    <div class="workspace">
      <header class="topbar">
        <div class="topbar-brand">
          <img :src="fresvelBrand" alt="Fresvel" class="topbar-logo" />
          <div class="topbar-copy">
            <strong>AQRisk Console</strong>
            <span>Monitoreo, evaluación difusa y explicabilidad operativa</span>
          </div>
        </div>
        <div class="topbar-status">
          <span class="status-pill" :class="healthStatusClass || 'status-neutral'">
            {{ isBackendReady ? "Backend operativo" : "Backend pendiente" }}
          </span>
          <span class="status-pill status-neutral">Modo {{ form.mode }}</span>
        </div>
      </header>

      <main class="content">
        <section class="page-head panel">
          <div class="page-head-copy">
            <span class="eyebrow">Centro de análisis</span>
            <h2>Panel de control y explicabilidad</h2>
            <p>
              Consolida la entrada, el estado normativo, la inferencia difusa y el ajuste contextual en una
              sola superficie de trabajo.
            </p>
          </div>
          <div class="page-head-side">
            <strong>Estado del backend</strong>
            <p :class="healthStatusClass">{{ healthMessage }}</p>
            <small>API: {{ apiBaseUrl }}</small>
            <p v-if="lastError" class="caption status-danger">{{ lastError }}</p>
            <div class="page-head-actions">
              <button class="secondary" type="button" @click="openSectionGuide(currentSection)">
                Cómo leer esta vista
              </button>
              <button v-if="result" class="secondary" type="button" @click="openResultGuide">
                Interpretar corrida
              </button>
              <button v-if="result" class="secondary" type="button" @click="exportCurrentRun">
                Exportar JSON
              </button>
            </div>
          </div>
        </section>

        <section class="grid-two">
        <section class="panel">
          <h3>Control de entrada</h3>
          <p class="caption">
            Selecciona el modo de ejecución y los parámetros mínimos de la consulta. Este formulario
            dispara la evaluación del artefacto.
          </p>
          <div class="form-grid">
            <div class="field">
              <label for="mode">Modo</label>
              <select id="mode" v-model="form.mode">
                <option v-for="mode in metadata.modes" :key="mode" :value="mode">
                  {{ mode }}
                </option>
              </select>
            </div>

            <div class="field" v-if="form.mode === 'mock'">
              <label for="scenarioId">Escenario de evaluación</label>
              <select id="scenarioId" v-model="form.scenario_id">
                <option v-for="item in scenarios" :key="item.scenario_id" :value="item.scenario_id">
                  {{ item.name }}
                </option>
              </select>
            </div>

            <div class="field" v-if="form.mode === 'openaq'">
              <label for="locationId">Location ID</label>
              <input id="locationId" v-model="form.location_id" type="number" placeholder="3175328" />
            </div>

            <div class="field">
              <label for="lookback">Ventana temporal (horas)</label>
              <input id="lookback" v-model="form.lookback_hours" type="number" min="1" />
            </div>

            <div class="field">
              <label for="coverage">Cobertura mínima (%)</label>
              <input id="coverage" v-model="form.min_coverage" type="number" min="1" max="100" />
            </div>

            <div class="input-hint">
              <strong>{{ executionGuide.title }}</strong>
              <p>{{ executionGuide.body }}</p>
            </div>

            <button class="primary" :disabled="submitting || !canRunEvaluation" @click="runEvaluation">
              {{ submitting ? "Ejecutando..." : "Ejecutar evaluación" }}
            </button>
          </div>
          <LocationPicker
            v-if="form.mode === 'openaq'"
            :filtered-locations="filteredLocations"
            :location-id="form.location_id"
            :location-search="locationSearch"
            :locations="locations"
            :selected-location-preset="selectedLocationPreset"
            @refresh-locations="refreshLocations"
            @select-location-card="selectLocationCard"
            @update:selected-location-preset="updateSelectedLocationPreset"
            @update:location-search="locationSearch = $event"
          />
        </section>

        <section class="stack">
          <ExecutivePanel
            v-if="result"
            :metrics="executiveMetrics"
            :narrative="currentRunNarrative"
            @open-section="openViewer"
          />

          <section class="panel">
            <h3>Resumen de la corrida actual</h3>
            <p class="caption">
              Síntesis del episodio analizado para lectura rápida y captura documental.
            </p>
            <div class="summary-grid">
              <article class="summary-item">
                <span>Fuente</span>
                <strong>{{ currentRunSummary.source }}</strong>
              </article>
              <article class="summary-item">
                <span>Entrada</span>
                <strong>{{ currentRunSummary.entry }}</strong>
              </article>
              <article class="summary-item">
                <span>Dominante</span>
                <strong>{{ currentRunSummary.dominant }}</strong>
              </article>
              <article class="summary-item">
                <span>Reglas activadas</span>
                <strong>{{ currentRunSummary.triggeredRules }}</strong>
              </article>
              <article class="summary-item">
                <span>Ajuste contextual</span>
                <strong>{{ currentRunSummary.context }}</strong>
              </article>
              <article class="summary-item">
                <span>Histórico local</span>
                <strong>{{ historyItems.length }}</strong>
              </article>
            </div>
          </section>

          <section class="panel">
            <h3>Base del modelo</h3>
            <p class="caption">Metadatos del backend expuestos para el frontend.</p>
            <div class="tag-list">
              <span v-for="layer in metadata.model.layers" :key="layer" class="tag">{{ layer }}</span>
            </div>
            <p class="caption" style="margin-top: 12px">
              Base normativa: {{ metadata.model.normative_basis }}. Reglas principales:
              {{ metadata.model.main_rule_count }}. Reglas contextuales:
              {{ metadata.model.context_rule_count }}.
            </p>
          </section>

          <section class="cards">
            <article
              v-for="item in statCards"
              :key="item.label"
              class="stat-card"
              :class="item.tone"
            >
              <span>{{ item.label }}</span>
              <strong>{{ item.value }}</strong>
              <small>{{ item.helper }}</small>
            </article>
          </section>
        </section>
        </section>

        <section v-if="result" class="panel">
          <h3>Exploración detallada</h3>
          <p class="caption">
            Usa el menú lateral o estos accesos rápidos para abrir una vista específica del sistema.
          </p>
          <div class="section-dock">
            <button
              v-for="item in sections"
              :key="item.id"
              class="section-dock-button"
              :class="{ active: currentSection === item.id }"
              type="button"
              @click="openViewer(item.id)"
            >
              <strong>{{ item.label }}</strong>
              <span>{{ sectionGuides[item.id]?.caption }}</span>
            </button>
          </div>
        </section>

        <section v-else class="empty-state">
          Aún no hay una corrida en memoria. Ejecuta la evaluación para poblar el panel y habilitar las vistas detalladas.
        </section>
      </main>
    </div>

    <div
      v-if="viewerOpen && result"
      class="modal-overlay"
      role="presentation"
      @click.self="closeViewer"
    >
      <section class="modal-card modal-card-wide" role="dialog" aria-modal="true" :aria-label="activeSectionLabel">
        <div class="modal-head">
          <div>
            <h3>{{ activeSectionLabel }}</h3>
            <p class="caption">Visor modal para revisar una sola sección del sistema a la vez.</p>
          </div>
          <div class="modal-head-actions">
            <div class="section-selector">
              <button
                v-for="item in sections"
                :key="item.id"
                class="section-chip"
                :class="{ active: currentSection === item.id }"
                type="button"
                @click="currentSection = item.id"
              >
                {{ item.label }}
              </button>
            </div>
          </div>
        </div>

        <div class="modal-body">
          <DashboardSection
            v-show="currentSection === 'dashboard'"
            :auxiliary-chart="auxiliaryChart"
            :available-series-parameters="availableSeriesParameters"
            :bar-options="barOptions"
            :base-vs-final-chart="baseVsFinalChart"
            :selected-series-parameter="selectedSeriesParameter"
            :series-line-options="seriesLineOptions"
            :subindices-chart="subindicesChart"
            :subindices-chart-options="subindicesChartOptions"
            :time-series-chart="timeSeriesChart"
            @update:selected-series-parameter="selectedSeriesParameter = $event"
          />

          <TraceabilitySection
            v-show="currentSection === 'traceability'"
            :activated-rule-details="activatedRuleDetails"
            :result="result"
            :sensors="sensors"
          />

          <ExplainabilitySection
            v-show="currentSection === 'explainability'"
            :aggregation-chart="aggregationChart"
            :aqi-membership-chart="aqiMembershipChart"
            :bar-options="barOptions"
            :concurrence-membership-chart="concurrenceMembershipChart"
            :context-trace="contextTrace"
            :line-options="lineOptions"
            :line-options-with-legend="lineOptionsWithLegend"
            :persistence-membership-chart="persistenceMembershipChart"
            :principal-trace="principalTrace"
            :result="result"
            :triggered-rules-chart="triggeredRulesChart"
          />

          <EvaluationSection
            v-show="currentSection === 'evaluation'"
            :active-history-filters="activeHistoryFilters"
            :bar-options="barOptions"
            :context-trace="contextTrace"
            :context-before-after-chart="contextBeforeAfterChart"
            :filtered-history-items="filteredHistoryItems"
            :history-coverage-chart="historyCoverageChart"
            :history-date-filter="historyDateFilter"
            :history-filter="historyFilter"
            :history-items="historyItems"
            :history-parameter-filter="historyParameterFilter"
            :history-parameters="historyParameters"
            :history-risk-filter="historyRiskFilter"
            :history-risk-labels="historyRiskLabels"
            :history-risk-comparison-chart="historyRiskComparisonChart"
            :principal-trace="principalTrace"
            :result="result"
            :selected-history-item="selectedHistoryItem"
            @reset-history-filters="resetHistoryFilters"
            @select-history-item="selectedHistoryItem = $event"
            @toggle-history-parameter="toggleHistoryParameter"
            @toggle-history-risk="toggleHistoryRisk"
            @update:history-date-filter="historyDateFilter = $event"
            @update:history-filter="historyFilter = $event"
            @update:history-parameter-filter="historyParameterFilter = $event"
            @update:history-risk-filter="historyRiskFilter = $event"
          />
        </div>
        <div class="modal-footer">
          <button class="danger-button" type="button" @click="closeViewer">Cerrar</button>
        </div>
      </section>
    </div>

    <div v-if="modalState.open" class="modal-overlay" role="presentation" @click.self="closeModal">
      <section class="modal-card" role="dialog" aria-modal="true" :aria-label="modalState.title">
        <div class="modal-head">
          <div>
            <h3>{{ modalState.title }}</h3>
            <p class="caption" v-if="modalState.caption">{{ modalState.caption }}</p>
          </div>
        </div>

        <div class="modal-body">
          <template v-if="modalState.mode === 'list'">
            <article v-for="item in modalState.items" :key="item.title" class="modal-block">
              <h4>{{ item.title }}</h4>
              <p>{{ item.body }}</p>
            </article>
          </template>

          <template v-else>
            <article v-for="item in modalState.items" :key="item.title" class="modal-block">
              <h4>{{ item.title }}</h4>
              <p>{{ item.body }}</p>
            </article>
          </template>
        </div>
        <div class="modal-footer">
          <button class="danger-button" type="button" @click="closeModal">Cerrar</button>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from "vue";
import DashboardSection from "./components/DashboardSection.vue";
import EvaluationSection from "./components/EvaluationSection.vue";
import ExplainabilitySection from "./components/ExplainabilitySection.vue";
import ExecutivePanel from "./components/ExecutivePanel.vue";
import LocationPicker from "./components/LocationPicker.vue";
import SidebarNav from "./components/SidebarNav.vue";
import TraceabilitySection from "./components/TraceabilitySection.vue";
import fresvelBrand from "./assets/fresvel-brand-top.png";
import { useHistoryFilters } from "./composables/useHistoryFilters";
import { useLocationSearch } from "./composables/useLocationSearch";
import { checkHealth, evaluateModule, fetchHistory, fetchLocationSensors, fetchLocations, fetchMetadata, fetchScenarios } from "./services/api";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:18010";
const sections = [
  { id: "dashboard", label: "Dashboard" },
  { id: "traceability", label: "Trazabilidad" },
  { id: "explainability", label: "Explicabilidad" },
  { id: "evaluation", label: "Evaluación" },
];

const currentSection = ref("dashboard");
const selectedSeriesParameter = ref("pm25");
const healthMessage = ref("Verificando servicio...");
const healthStatusClass = ref("");
const lastError = ref("");
const submitting = ref(false);
const result = ref(null);
const locations = ref([]);
const sensors = ref([]);
const historyItems = ref([]);
const historyFilter = ref("");
const historyDateFilter = ref("");
const historyParameterFilter = ref("");
const historyRiskFilter = ref("");
const selectedHistoryItem = ref(null);
const selectedLocationPreset = ref("");
const locationSearch = ref("");
const scenarios = ref([]);
const viewerOpen = ref(false);
const modalState = reactive({
  open: false,
  title: "",
  caption: "",
  mode: "list",
  items: [],
});
const captureMode = ref(false);

const metadata = reactive({
  modes: ["mock", "openaq"],
  default_config: {
    mode: "mock",
    location_id: "",
    lookback_hours: 24,
    min_coverage: 80,
    scenario_id: "urban_escalation",
  },
  model: {
    normative_basis: "EPA/AQS AQI Breakpoints",
    supported_parameters: [],
    context_parameters: [],
    main_rule_count: 54,
    context_rule_count: 9,
    layers: [],
    membership_curves: {
      aqi: {},
      persistence: {},
      concurrence: {},
      risk: {},
    },
  },
});

const form = reactive({
  mode: "mock",
  location_id: "",
  lookback_hours: 24,
  min_coverage: 80,
  scenario_id: "urban_escalation",
});

const barOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
  },
  scales: {
    x: { grid: { display: false }, ticks: { color: "#627079" } },
    y: {
      beginAtZero: true,
      grid: { color: "rgba(23, 33, 39, 0.08)" },
      ticks: { color: "#627079" },
    },
  },
};

const lineOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
  },
  scales: {
    x: { type: "linear", grid: { color: "rgba(23, 33, 39, 0.08)" }, ticks: { color: "#627079" } },
    y: { beginAtZero: true, max: 1.05, grid: { color: "rgba(23, 33, 39, 0.08)" }, ticks: { color: "#627079" } },
  },
};

const lineOptionsWithLegend = {
  ...lineOptions,
  plugins: {
    legend: { display: true, position: "bottom" },
  },
};

const seriesLineOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
  },
  scales: {
    x: { grid: { color: "rgba(23, 33, 39, 0.06)" } },
    y: { beginAtZero: true, grid: { color: "rgba(23, 33, 39, 0.06)" } },
  },
};

const palette = ["#2fb7d3", "#0f8f8a", "#46b34d", "#d38b1e", "#d15e43", "#202738"];
const aqiThresholds = [
  { label: "Bueno", value: 50, color: "#46b34d" },
  { label: "Moderado", value: 100, color: "#d38b1e" },
  { label: "Sensibles", value: 150, color: "#d15e43" },
  { label: "Dañino", value: 200, color: "#9a3412" },
];

function classifyAqiBand(value) {
  if (value <= 50) {
    return "good";
  }
  if (value <= 100) {
    return "moderate";
  }
  if (value <= 150) {
    return "unhealthy_sensitive_groups";
  }
  if (value <= 200) {
    return "unhealthy";
  }
  if (value <= 300) {
    return "very_unhealthy";
  }
  return "hazardous";
}

function aqiBandColor(value, isDominant = false) {
  const paletteByBand = {
    good: isDominant ? "#2c9a47" : "#83cf7a",
    moderate: isDominant ? "#c47d13" : "#e5b85f",
    unhealthy_sensitive_groups: isDominant ? "#cf6447" : "#ef9d86",
    unhealthy: isDominant ? "#9a3412" : "#c96b4f",
    very_unhealthy: isDominant ? "#5b2c83" : "#8d63b0",
    hazardous: isDominant ? "#202738" : "#4d556b",
  };
  return paletteByBand[classifyAqiBand(value)];
}

const isBackendReady = computed(() => healthStatusClass.value === "status-ok");
const selectedScenarioName = computed(
  () => scenarios.value.find((item) => item.scenario_id === form.scenario_id)?.name || form.scenario_id,
);
const hasContextAdjustments = computed(() => Boolean(result.value?.context_adjustments?.length));
const contextualDelta = computed(() => {
  const baseScore = Number(
    result.value?.explainability?.layer_outputs?.inferencia_difusa_principal?.score || 0,
  );
  const finalScore = Number(result.value?.fuzzy?.score || 0);
  return Number((finalScore - baseScore).toFixed(2));
});
const riskTone = computed(() => {
  const label = String(result.value?.fuzzy?.label || "").toLowerCase();
  const score = Number(result.value?.fuzzy?.score || 0);
  if (label.includes("alto") || score >= 150) {
    return "tone-danger";
  }
  if (label.includes("moder") || score >= 100) {
    return "tone-warn";
  }
  return "tone-ok";
});
const coverageTone = computed(() => {
  const coverage = Number(result.value?.snapshot?.coverage_global || 0);
  return coverage >= Number(form.min_coverage || 0) ? "tone-ok" : "tone-warn";
});
const {
  filteredLocations,
  selectLocationCard,
  selectedLocationName,
  updateSelectedLocationPreset,
} = useLocationSearch({
  locations,
  form,
  result,
  selectedLocationPreset,
  locationSearch,
  loadSensors,
});

const {
  activeHistoryFilters,
  filteredHistoryItems,
  historyParameters,
  historyRiskLabels,
  resetHistoryFilters,
  toggleHistoryParameter,
  toggleHistoryRisk,
} = useHistoryFilters({
  historyItems,
  historyFilter,
  historyDateFilter,
  historyParameterFilter,
  historyRiskFilter,
  selectedHistoryItem,
});

const canRunEvaluation = computed(() => {
  if (form.mode === "openaq") {
    return Boolean(form.location_id);
  }
  return Boolean(form.scenario_id);
});
const executionGuide = computed(() => {
  if (form.mode === "mock") {
    return {
      title: "Modo controlado",
      body: "Úsalo para demostración, capturas y validación repetible del comportamiento del artefacto.",
    };
  }
  return {
    title: "Modo OpenAQ",
    body: "Requiere un location ID válido. Conviene para evidenciar consumo real de datos y trazabilidad de sensores.",
  };
});

const currentRunSummary = computed(() => ({
  source: form.mode === "mock" ? "Escenario controlado" : "OpenAQ",
  entry:
    form.mode === "mock"
      ? selectedScenarioName.value
      : selectedLocationName.value,
  dominant: result.value?.aqi?.dominant_parameter || "sin dominante",
  triggeredRules: String(result.value?.fuzzy?.triggered_rules?.length || 0),
  context:
    result.value && result.value.context_adjustments.length > 0
      ? `${result.value.context_adjustments.length} ajuste(s)`
      : "Sin ajuste",
}));

const activeSectionLabel = computed(
  () => sections.find((item) => item.id === currentSection.value)?.label || "Visor",
);
const executiveMetrics = computed(() => {
  if (!result.value) {
    return [];
  }
  return [
    {
      label: "Riesgo final",
      value: result.value.fuzzy?.label || "NR",
      helper: `Puntuación ${result.value.fuzzy?.score ?? "NR"}`,
      tone: riskTone.value,
    },
    {
      label: "AQI dominante",
      value: `${result.value.aqi?.global_aqi ?? "NR"} · ${result.value.aqi?.dominant_parameter || "sin dominante"}`,
      helper: result.value.aqi?.category || "Sin categoría",
      tone: "tone-info",
    },
    {
      label: "Cobertura",
      value: `${result.value.snapshot?.coverage_global ?? "NR"}%`,
      helper:
        Number(result.value.snapshot?.coverage_global || 0) >= Number(form.min_coverage || 0)
          ? "Cumple el umbral configurado"
          : "Queda por debajo del umbral configurado",
      tone:
        Number(result.value.snapshot?.coverage_global || 0) >= Number(form.min_coverage || 0)
          ? "tone-ok"
          : "tone-warn",
    },
    {
      label: "Capa contextual",
      value: hasContextAdjustments.value ? `${contextualDelta.value > 0 ? "+" : ""}${contextualDelta.value}` : "Sin cambios",
      helper: hasContextAdjustments.value ? `${result.value.context_adjustments.length} ajuste(s)` : "No hubo modulación adicional",
      tone: hasContextAdjustments.value ? "tone-warn" : "tone-ok",
    },
  ];
});
const currentRunNarrative = computed(() => {
  if (!result.value) {
    return {
      title: "Sistema listo para una nueva corrida",
      body: "Configura un escenario o una ubicación real para poblar el panel con evidencia trazable.",
    };
  }
  return {
    title: `${result.value.fuzzy?.label || "Riesgo no disponible"} en ${currentRunSummary.value.entry}`,
    body: `El episodio queda dominado por ${result.value.aqi?.dominant_parameter || "sin parámetro dominante"} con AQI ${
      result.value.aqi?.global_aqi ?? "NR"
    }, ${activatedRuleDetails.value.length} regla(s) activada(s) y cobertura ${
      result.value.snapshot?.coverage_global ?? "NR"
    }%. ${hasContextAdjustments.value ? "La capa contextual modificó la salida final." : "La capa contextual no alteró la salida principal."}`,
  };
});
const statCards = computed(() => [
  {
    label: "AQI global",
    value: result.value?.aqi?.global_aqi ?? "—",
    helper: result.value?.aqi?.dominant_parameter || "Sin dominante",
    tone: "tone-info",
  },
  {
    label: "Categoría base",
    value: result.value?.aqi?.category ?? "—",
    helper: metadata.model.normative_basis,
    tone: "tone-neutral",
  },
  {
    label: "Riesgo final",
    value: result.value?.fuzzy?.label ?? "—",
    helper: `Score ${result.value?.fuzzy?.score ?? "—"}`,
    tone: riskTone.value,
  },
  {
    label: "Cobertura global",
    value: result.value?.snapshot?.coverage_global ?? "—",
    helper: `Umbral ${form.min_coverage}%`,
    tone:
      Number(result.value?.snapshot?.coverage_global || 0) >= Number(form.min_coverage || 0)
        ? "tone-ok"
        : "tone-warn",
  },
]);

const sectionGuides = {
  dashboard: {
    title: "Cómo leer el dashboard",
    caption: "Esta vista resume el episodio actual y muestra la progresión desde la entrada hasta la salida del sistema.",
    items: [
      {
        title: "Qué mirar primero",
        body: "Empieza por el resumen de la corrida y las cuatro tarjetas superiores. Ahí se concentra el AQI global, la categoría base, el riesgo final y la cobertura del episodio.",
      },
      {
        title: "Cómo leer las gráficas",
        body: "La serie temporal muestra el comportamiento reciente del parámetro seleccionado. La gráfica de subíndices permite identificar el contaminante dominante. La comparación AQI base frente a salida final muestra si el motor difuso endureció o mantuvo la lectura inicial.",
      },
      {
        title: "Qué decisión permite",
        body: "Esta vista permite decidir si el episodio requiere una revisión más profunda en trazabilidad o explicabilidad y si la salida final es coherente con la fuente de datos y la cobertura disponible.",
      },
    ],
  },
  traceability: {
    title: "Cómo leer la trazabilidad",
    caption: "Esta vista expone el recorrido completo de la decisión y los elementos observados por el sistema.",
    items: [
      {
        title: "Ruta de decisión",
        body: "La ruta de decisión enumera las cinco capas del artefacto. Sirve para ubicar en qué etapa se consolidó el AQI, en cuál se activó la base difusa y si hubo ajuste contextual.",
      },
      {
        title: "Parámetros y sensores",
        body: "Los parámetros soportados y no soportados permiten identificar qué parte de la entrada fue usada en el cálculo normativo. La lista de sensores ayuda a verificar la estructura real de la estación consultada.",
      },
      {
        title: "Reglas y ajustes",
        body: "La lista de reglas activadas muestra qué reglas participaron y con qué fuerza. Los ajustes contextuales permiten justificar por qué la salida final se mantuvo o cambió frente a la clasificación base.",
      },
    ],
  },
  explainability: {
    title: "Cómo leer la explicabilidad",
    caption: "Esta vista describe el comportamiento interno del modelo difuso.",
    items: [
      {
        title: "Funciones de pertenencia",
        body: "Las curvas de AQI, concurrencia y persistencia muestran cómo el sistema representa lingüísticamente las entradas. Cada término activa una zona distinta del razonamiento.",
      },
      {
        title: "Reglas activadas",
        body: "La distribución de reglas activadas permite identificar qué fragmentos de la base principal participaron en la corrida. No todas las reglas se activan con la misma fuerza en cada episodio.",
      },
      {
        title: "Defuzzificación",
        body: "La gráfica de agregación y defuzzificación muestra la salida continua del sistema antes de traducirla a una etiqueta final. Esa puntuación explica por qué la salida se ubicó en una clase específica.",
      },
    ],
  },
  evaluation: {
    title: "Cómo leer la evaluación",
    caption: "Esta vista ayuda a contrastar la corrida actual con su historial y a revisar el impacto del ajuste contextual.",
    items: [
      {
        title: "Alerta final",
        body: "El bloque superior resume el mensaje operativo del sistema. Debe leerse junto con la categoría final y la cobertura disponible.",
      },
      {
        title: "Antes y después",
        body: "La comparación antes y después muestra si la capa contextual modificó la salida principal del motor difuso o si la mantuvo.",
      },
      {
        title: "Histórico",
        body: "El histórico local permite comparar episodios y verificar estabilidad entre corridas. Los filtros ayudan a recuperar estaciones, fechas o contaminantes dominantes específicos.",
      },
    ],
  },
};

const subindicesChart = computed(() => {
  const labels = Object.keys(result.value?.aqi?.subindices || {});
  const dominant = result.value?.aqi?.dominant_parameter;
  const values = labels.map((label) => result.value.aqi.subindices[label]);
  return {
    labels,
    datasets: [
      {
        label: "Subíndice AQI",
        data: values,
        backgroundColor: labels.map((label, index) => aqiBandColor(values[index], label === dominant)),
        borderColor: labels.map((label, index) =>
          label === dominant ? "#202738" : aqiBandColor(values[index], true),
        ),
        borderWidth: labels.map((label) => (label === dominant ? 2 : 1)),
        borderRadius: 6,
      },
      ...aqiThresholds
        .filter((item) => !values.length || Math.max(...values, 0) >= item.value - 20)
        .map((item) => ({
          type: "line",
          label: `Umbral ${item.label} (${item.value})`,
          data: labels.map(() => item.value),
          borderColor: item.color,
          borderDash: [6, 6],
          borderWidth: 1.5,
          pointRadius: 0,
          pointHoverRadius: 0,
          fill: false,
        })),
    ],
  };
});

const subindicesChartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: "bottom",
      labels: {
        color: "#627079",
        boxWidth: 18,
      },
    },
  },
  scales: {
    x: { grid: { display: false }, ticks: { color: "#627079" } },
    y: {
      beginAtZero: true,
      suggestedMax: Math.max(result.value?.aqi?.global_aqi || 0, 160),
      grid: { color: "rgba(23, 33, 39, 0.08)" },
      ticks: { color: "#627079" },
      title: {
        display: true,
        text: "Subíndice AQI",
        color: "#627079",
      },
    },
  },
}));

const baseVsFinalChart = computed(() => ({
  labels: ["AQI base", "Puntuación difusa"],
  datasets: [
    {
      data: [result.value?.aqi?.global_aqi || 0, result.value?.fuzzy?.score || 0],
      backgroundColor: ["#2fb7d3", "#46b34d"],
      borderRadius: 6,
    },
  ],
}));

const auxiliaryChart = computed(() => ({
  labels: ["Concurrencia", "Persistencia", "Cobertura"],
  datasets: [
    {
      data: [
        result.value?.concurrence_score || 0,
        result.value?.persistence_score || 0,
        result.value?.snapshot?.coverage_global || 0,
      ],
      backgroundColor: ["#d38b1e", "#d15e43", "#46b34d"],
      borderRadius: 6,
    },
  ],
}));

const activatedRuleDetails = computed(() => {
  const rules = result.value?.explainability?.layer_outputs?.inferencia_difusa_principal?.rules || [];
  return [...rules]
    .sort((left, right) => right.strength - left.strength)
    .map((rule) => ({
      ...rule,
      strengthLabel: Number(rule.strength).toFixed(2),
      outputLabel: String(rule.output_term || "").replaceAll("_", " "),
    }));
});

const triggeredRulesChart = computed(() => ({
  labels: activatedRuleDetails.value.length
    ? activatedRuleDetails.value.map((rule) => rule.name)
    : ["sin reglas"],
  datasets: [
    {
      data: activatedRuleDetails.value.length
        ? activatedRuleDetails.value.map((rule) => rule.strength)
        : [0],
      backgroundColor: "#2fb7d3",
      borderRadius: 6,
    },
  ],
}));

const availableSeriesParameters = computed(() => Object.keys(result.value?.snapshot?.series || {}));
const principalTrace = computed(
  () => result.value?.explainability?.layer_outputs?.inferencia_difusa_principal || {},
);
const contextTrace = computed(
  () => result.value?.explainability?.layer_outputs?.ajuste_contextual || {},
);

const timeSeriesChart = computed(() => {
  const observations = result.value?.snapshot?.series?.[selectedSeriesParameter.value]?.observations || [];
  return {
    labels: observations.map((item) => item.datetime_to),
    datasets: [
      {
        label: selectedSeriesParameter.value,
        data: observations.map((item) => item.value),
        borderColor: "#0f8f8a",
        backgroundColor: "rgba(15, 143, 138, 0.14)",
        fill: true,
        tension: 0.22,
      },
    ],
  };
});

const aggregationChart = computed(() => {
  const points = principalTrace.value?.aggregation_samples || [];
  const principalScoreValue = principalTrace.value?.score || 0;
  const nearestSample =
    points.reduce(
      (best, item) =>
        Math.abs(item.x - principalScoreValue) < Math.abs(best.x - principalScoreValue) ? item : best,
      { x: 0, membership: 0 },
    ) || { x: principalScoreValue, membership: 0 };
  return {
    datasets: [
      {
        label: "Agregación difusa",
        data: points.map((item) => ({ x: item.x, y: item.membership })),
        borderColor: "#202738",
        backgroundColor: "rgba(32, 39, 56, 0.14)",
        fill: true,
        tension: 0.25,
      },
      {
        label: "Score principal",
        data: [{ x: principalScoreValue, y: nearestSample.membership || 0 }],
        borderColor: "#d15e43",
        backgroundColor: "#d15e43",
        pointRadius: 5,
        pointHoverRadius: 6,
        showLine: false,
      },
    ],
  };
});

const contextBeforeAfterChart = computed(() => {
  const before = result.value?.explainability?.layer_outputs?.inferencia_difusa_principal?.score || 0;
  const after = result.value?.fuzzy?.score || 0;
  return {
    labels: ["Salida principal", "Salida final"],
    datasets: [
      {
        data: [before, after],
        backgroundColor: ["#d38b1e", "#46b34d"],
        borderRadius: 6,
      },
    ],
  };
});

const historyRiskComparisonChart = computed(() => {
  const current = result.value;
  const previous = selectedHistoryItem.value;
  return {
    labels: ["AQI base", "Puntuación final"],
    datasets: [
      {
        label: "Actual",
        data: [
          current?.aqi?.global_aqi || 0,
          current?.fuzzy?.score || 0,
        ],
        backgroundColor: "#2fb7d3",
        borderRadius: 6,
      },
      {
        label: "Histórica",
        data: [
          previous?.summary?.aqi_global || 0,
          previous?.summary?.fuzzy_score || 0,
        ],
        backgroundColor: "#0f8f8a",
        borderRadius: 6,
      },
    ],
  };
});

const historyCoverageChart = computed(() => {
  const current = result.value;
  const previous = selectedHistoryItem.value;
  return {
    labels: ["Cobertura"],
    datasets: [
      {
        label: "Actual",
        data: [current?.snapshot?.coverage_global || 0],
        backgroundColor: "#46b34d",
        borderRadius: 6,
      },
      {
        label: "Histórica",
        data: [previous?.summary?.coverage_global || 0],
        backgroundColor: "#d38b1e",
        borderRadius: 6,
      },
    ],
  };
});

function buildMembershipChart(curves, inputValue) {
  const entries = Object.entries(curves || {});
  return {
    datasets: [
      ...entries.map(([term, points], index) => ({
        label: term,
        data: points.map((item) => ({ x: item.x, y: item.membership })),
        borderColor: palette[index % palette.length],
        backgroundColor: "transparent",
        tension: 0.22,
      })),
      ...(typeof inputValue === "number" && Number.isFinite(inputValue)
        ? [
            {
              label: "entrada actual",
              data: [
                { x: inputValue, y: 0 },
                { x: inputValue, y: 1 },
              ],
              borderColor: "#202738",
              borderDash: [6, 4],
              pointRadius: 0,
              fill: false,
              tension: 0,
            },
          ]
        : []),
    ],
  };
}

const aqiMembershipChart = computed(() =>
  buildMembershipChart(metadata.model.membership_curves?.aqi, principalTrace.value?.inputs?.aqi),
);
const concurrenceMembershipChart = computed(() =>
  buildMembershipChart(
    metadata.model.membership_curves?.concurrence,
    principalTrace.value?.inputs?.concurrence,
  ),
);
const persistenceMembershipChart = computed(() =>
  buildMembershipChart(
    metadata.model.membership_curves?.persistence,
    principalTrace.value?.inputs?.persistence,
  ),
);

async function loadMetadata() {
  try {
    const payload = await fetchMetadata();
    Object.assign(metadata, payload);
    form.mode = payload.default_config.mode;
    form.location_id = payload.default_config.location_id ?? "";
    form.lookback_hours = payload.default_config.lookback_hours;
    form.min_coverage = payload.default_config.min_coverage;
    form.scenario_id = payload.default_config.scenario_id || "urban_escalation";
  } catch (error) {
    healthMessage.value = "No se pudo cargar metadata del backend.";
    healthStatusClass.value = "status-danger";
  }
}

async function refreshLocations() {
  try {
    const payload = await fetchLocations();
    locations.value = payload.items || [];
  } catch (error) {
    locations.value = [];
  }
}

async function loadSensors(locationId) {
  if (!locationId) {
    sensors.value = [];
    return;
  }
  try {
    const payload = await fetchLocationSensors(locationId);
    sensors.value = payload.items || [];
  } catch (error) {
    sensors.value = [];
  }
}

async function refreshHistory() {
  try {
    const payload = await fetchHistory();
    historyItems.value = payload.items || [];
  } catch (error) {
    historyItems.value = [];
  }
}

async function refreshScenarios() {
  try {
    const payload = await fetchScenarios();
    scenarios.value = payload.items || [];
  } catch (error) {
    scenarios.value = [];
  }
}

function openSectionGuide(sectionId) {
  const guide = sectionGuides[sectionId];
  if (!guide) {
    return;
  }
  modalState.open = true;
  modalState.title = guide.title;
  modalState.caption = guide.caption;
  modalState.mode = "list";
  modalState.items = guide.items;
}

function openResultGuide() {
  if (!result.value) {
    return;
  }
  modalState.open = true;
  modalState.title = "Interpretación de la corrida actual";
  modalState.caption = "Lectura guiada del resultado producido por el artefacto.";
  modalState.mode = "list";
  modalState.items = [
    {
      title: "Estado base",
      body: `El AQI normativo calculado es ${result.value.aqi.global_aqi} y la categoría base es ${result.value.aqi.category}. Esta es la referencia inicial del episodio.`,
    },
    {
      title: "Dominancia y apoyo difuso",
      body: `El contaminante dominante es ${result.value.aqi.dominant_parameter || "NR"}. La concurrencia es ${result.value.concurrence_score} y la persistencia es ${result.value.persistence_score}. Estas variables alimentan la base principal de 54 reglas.`,
    },
    {
      title: "Salida del sistema",
      body: `La salida final es ${result.value.fuzzy.label} con una puntuación de ${result.value.fuzzy.score}. ${result.value.context_adjustments.length > 0 ? "La capa contextual introdujo ajustes adicionales." : "La capa contextual no modificó la salida principal."}`,
    },
    {
      title: "Lectura operativa",
      body: result.value.alert.message,
    },
  ];
}

function closeModal() {
  modalState.open = false;
}

function exportCurrentRun() {
  if (!result.value) {
    return;
  }
  const payload = {
    exported_at: new Date().toISOString(),
    request: {
      mode: form.mode,
      location_id: form.location_id || null,
      lookback_hours: Number(form.lookback_hours),
      min_coverage: Number(form.min_coverage),
      scenario_id: form.scenario_id,
    },
    response: result.value,
  };
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `aqrisk-run-${new Date().toISOString().slice(0, 19).replaceAll(":", "-")}.json`;
  link.click();
  URL.revokeObjectURL(url);
}

function openViewer(sectionId) {
  if (!result.value) {
    return;
  }
  currentSection.value = sectionId;
  viewerOpen.value = true;
}

function closeViewer() {
  viewerOpen.value = false;
}

function parseBooleanParam(value) {
  return value === "1" || value === "true" || value === "yes";
}

function readCaptureConfig() {
  if (typeof window === "undefined") {
    return null;
  }
  const params = new URLSearchParams(window.location.search);
  const mode = params.get("mode");
  const section = params.get("viewer");
  const scenarioId = params.get("scenario_id");
  const locationId = params.get("location_id");
  const series = params.get("series");
  const autorun = parseBooleanParam(params.get("autorun") || params.get("capture") || "");
  const enabled = parseBooleanParam(params.get("capture") || "") || autorun || Boolean(section);
  if (!enabled) {
    return null;
  }
  return {
    enabled,
    autorun,
    mode,
    section,
    scenarioId,
    locationId,
    series,
  };
}

async function applyCaptureConfig(config) {
  if (!config) {
    return;
  }
  captureMode.value = true;
  if (typeof document !== "undefined") {
    document.body.dataset.captureMode = "true";
  }
  if (config.mode && metadata.modes.includes(config.mode)) {
    form.mode = config.mode;
  }
  if (config.scenarioId) {
    form.scenario_id = config.scenarioId;
  }
  if (config.locationId) {
    form.location_id = config.locationId;
  }
  if (config.series) {
    selectedSeriesParameter.value = config.series;
  }
  if (config.autorun) {
    await runEvaluation();
    await nextTick();
  }
  if (config.section && sections.some((item) => item.id === config.section) && result.value) {
    currentSection.value = config.section;
    viewerOpen.value = true;
    await nextTick();
  }
}

async function loadHealth() {
  try {
    await checkHealth();
    healthMessage.value = "Servicio disponible.";
    healthStatusClass.value = "status-ok";
    lastError.value = "";
  } catch (error) {
    healthMessage.value = "Backend no disponible.";
    healthStatusClass.value = "status-danger";
    lastError.value = error?.message || "No fue posible establecer conexión con la API.";
  }
}

async function runEvaluation() {
  submitting.value = true;
  lastError.value = "";
  try {
    const payload = {
      mode: form.mode,
      location_id: form.mode === "openaq" && form.location_id !== "" ? Number(form.location_id) : null,
      lookback_hours: Number(form.lookback_hours),
      min_coverage: Number(form.min_coverage),
      scenario_id: form.scenario_id,
    };
    result.value = await evaluateModule(payload);
    currentSection.value = "dashboard";
    await refreshHistory();
    if (payload.location_id) {
      await loadSensors(payload.location_id);
    }
  } catch (error) {
    const detail = error?.response?.data?.error || error.message;
    healthMessage.value = detail;
    healthStatusClass.value = "status-danger";
    lastError.value = detail;
  } finally {
    submitting.value = false;
  }
}

function handleGlobalKeydown(event) {
  if (event.key !== "Escape") {
    return;
  }
  if (modalState.open) {
    closeModal();
    return;
  }
  if (viewerOpen.value) {
    closeViewer();
  }
}

onMounted(async () => {
  window.addEventListener("keydown", handleGlobalKeydown);
  await Promise.all([loadMetadata(), loadHealth(), refreshLocations(), refreshHistory(), refreshScenarios()]);
  await applyCaptureConfig(readCaptureConfig());
});

onBeforeUnmount(() => {
  window.removeEventListener("keydown", handleGlobalKeydown);
  if (typeof document !== "undefined") {
    delete document.body.dataset.captureMode;
  }
});

watch(
  availableSeriesParameters,
  (items) => {
    if (!items.length) {
      selectedSeriesParameter.value = "pm25";
      return;
    }
    if (!items.includes(selectedSeriesParameter.value)) {
      selectedSeriesParameter.value = items[0];
    }
  },
  { immediate: true },
);

watch(
  () => form.location_id,
  (value) => {
    if (form.mode !== "openaq" || value === "" || value === null) {
      return;
    }
    loadSensors(Number(value));
  },
);

watch(
  () => form.mode,
  (mode) => {
    lastError.value = "";
    if (mode === "mock") {
      sensors.value = [];
      locationSearch.value = "";
      return;
    }
    if (form.location_id) {
      loadSensors(Number(form.location_id));
    }
  },
);
</script>
