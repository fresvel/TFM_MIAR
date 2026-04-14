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
              <select id="locationId" :value="form.location_id" @change="handleLocationSelection($event.target.value)">
                <option value="">Seleccionar estación</option>
                <optgroup
                  v-if="openaqLocationOptions.curated.length"
                  label="Estaciones usadas en resultados"
                >
                  <option
                    v-for="item in openaqLocationOptions.curated"
                    :key="item.value"
                    :value="item.value"
                  >
                    {{ item.label }} · ID {{ item.value }}
                  </option>
                </optgroup>
                <optgroup
                  v-if="openaqLocationOptions.dynamic.length"
                  label="Ubicaciones cargadas"
                >
                  <option
                    v-for="item in openaqLocationOptions.dynamic"
                    :key="item.value"
                    :value="item.value"
                  >
                    {{ item.label }} · ID {{ item.value }}
                  </option>
                </optgroup>
              </select>
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
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from "vue";
import DashboardSection from "./components/DashboardSection.vue";
import EvaluationSection from "./components/EvaluationSection.vue";
import ExplainabilitySection from "./components/ExplainabilitySection.vue";
import ExecutivePanel from "./components/ExecutivePanel.vue";
import LocationPicker from "./components/LocationPicker.vue";
import SidebarNav from "./components/SidebarNav.vue";
import TraceabilitySection from "./components/TraceabilitySection.vue";
import fresvelBrand from "./assets/fresvel-brand-top.png";
import { BAR_OPTIONS, LINE_OPTIONS, LINE_OPTIONS_WITH_LEGEND, SERIES_LINE_OPTIONS } from "./config/chartOptions";
import { REPORT_OPENAQ_STATIONS } from "./config/openaqStations";
import { SECTION_GUIDES, SECTIONS } from "./config/sections";
import { useCaptureMode } from "./composables/useCaptureMode";
import { useHistoryFilters } from "./composables/useHistoryFilters";
import { useLocationSearch } from "./composables/useLocationSearch";
import { useResultCharts } from "./composables/useResultCharts";
import { useResultPresentation } from "./composables/useResultPresentation";
import { useWorkspaceData } from "./composables/useWorkspaceData";
import { downloadJson } from "./utils/download";

const currentSection = ref("dashboard");
const selectedSeriesParameter = ref("pm25");
const historyFilter = ref("");
const historyDateFilter = ref("");
const historyParameterFilter = ref("");
const historyRiskFilter = ref("");
const selectedHistoryItem = ref(null);
const selectedLocationPreset = ref("");
const locationSearch = ref("");
const viewerOpen = ref(false);
const modalState = reactive({
  open: false,
  title: "",
  caption: "",
  mode: "list",
  items: [],
});
const sections = SECTIONS;
const sectionGuides = SECTION_GUIDES;
const barOptions = BAR_OPTIONS;
const lineOptions = LINE_OPTIONS;
const lineOptionsWithLegend = LINE_OPTIONS_WITH_LEGEND;
const seriesLineOptions = SERIES_LINE_OPTIONS;
const reportOpenaqStations = REPORT_OPENAQ_STATIONS;

const {
  apiBaseUrl,
  canRunEvaluation,
  executionGuide,
  form,
  healthMessage,
  healthStatusClass,
  historyItems,
  initializeWorkspace,
  isBackendReady,
  lastError,
  loadSensors,
  locations,
  metadata,
  refreshHistory,
  result,
  runEvaluation,
  scenarios,
  sensors,
  submitting,
} = useWorkspaceData();

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

const openaqLocationOptions = computed(() => {
  const curated = reportOpenaqStations.map((item) => ({
    value: String(item.id),
    label: `${item.label} · ${item.city} · ${item.country}`,
    group: "Resultados del informe",
  }));
  const dynamic = locations.value
    .filter((item) => !reportOpenaqStations.some((station) => String(station.id) === String(item.id)))
    .map((item) => ({
      value: String(item.id),
      label: `${item.name}${item.city ? ` · ${item.city}` : ""}${item.country ? ` · ${item.country}` : ""}`,
      group: "Ubicaciones cargadas",
    }));
  return { curated, dynamic };
});

const {
  activatedRuleDetails,
  activeSectionLabel,
  contextTrace,
  coverageTone,
  currentRunNarrative,
  currentRunSummary,
  contextualDelta,
  executiveMetrics,
  hasContextAdjustments,
  principalTrace,
  riskTone,
  statCards,
} = useResultPresentation({
  currentSection,
  form,
  metadata,
  result,
  scenarios,
  sections,
  selectedLocationName,
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
const {
  aggregationChart,
  aqiMembershipChart,
  auxiliaryChart,
  availableSeriesParameters,
  baseVsFinalChart,
  concurrenceMembershipChart,
  contextBeforeAfterChart,
  historyCoverageChart,
  historyRiskComparisonChart,
  persistenceMembershipChart,
  subindicesChart,
  subindicesChartOptions,
  timeSeriesChart,
  triggeredRulesChart,
} = useResultCharts({
  metadata,
  principalTrace,
  result,
  selectedHistoryItem,
  selectedSeriesParameter,
});

const {
  applyCaptureConfig,
  clearCaptureMode,
  readCaptureConfig,
} = useCaptureMode({
  currentSection,
  form,
  metadata,
  result,
  runEvaluation,
  sections,
  selectedSeriesParameter,
  viewerOpen,
});

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
  downloadJson({
    exported_at: new Date().toISOString(),
    request: {
      mode: form.mode,
      location_id: form.location_id || null,
      lookback_hours: Number(form.lookback_hours),
      min_coverage: Number(form.min_coverage),
      scenario_id: form.scenario_id,
    },
    response: result.value,
  });
}

function handleLocationSelection(value) {
  form.location_id = value;
  selectedLocationPreset.value = value;
  if (!value) {
    sensors.value = [];
    return;
  }
  loadSensors(Number(value));
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
  await initializeWorkspace();
  await applyCaptureConfig(readCaptureConfig());
});

onBeforeUnmount(() => {
  window.removeEventListener("keydown", handleGlobalKeydown);
  clearCaptureMode();
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
    selectedLocationPreset.value = value ? String(value) : "";
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
