<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <h1>AQRisk Console</h1>
        <p>Control web del módulo de monitoreo, evaluación difusa y explicabilidad del artefacto.</p>
      </div>

      <div class="nav-group">
        <button
          v-for="item in sections"
          :key="item.id"
          class="nav-button"
          :class="{ active: currentSection === item.id, disabled: !result }"
          :disabled="!result"
          @click="openViewer(item.id)"
        >
          {{ item.label }}
        </button>
      </div>
    </aside>

    <main class="content">
      <section class="hero">
        <div class="hero-copy">
          <h2>Panel de control y explicabilidad</h2>
          <p>
            Esta interfaz actúa como controlador entre la selección de entrada, el consumo del backend
            AQRisk y la visualización del resultado. La salida se organiza por capas para exponer el
            estado normativo, las variables auxiliares, la inferencia difusa y el ajuste contextual.
          </p>
        </div>
        <div class="hero-status">
          <strong>Estado del backend</strong>
          <p :class="healthStatusClass">{{ healthMessage }}</p>
          <small>API: {{ apiBaseUrl }}</small>
          <div class="hero-actions">
            <button class="secondary" type="button" @click="openSectionGuide(currentSection)">
              Cómo leer esta vista
            </button>
            <button v-if="result" class="secondary" type="button" @click="openResultGuide">
              Interpretar esta corrida
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
              <label for="locationPreset">Ubicación sugerida</label>
              <select id="locationPreset" v-model="selectedLocationPreset" @change="applySelectedLocation">
                <option value="">Seleccionar ubicación</option>
                <option v-for="item in locations" :key="item.id" :value="String(item.id)">
                  {{ item.name }}{{ item.city ? ` · ${item.city}` : "" }}
                </option>
              </select>
            </div>

            <div class="field">
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

            <button class="primary" :disabled="submitting" @click="runEvaluation">
              {{ submitting ? "Ejecutando..." : "Ejecutar evaluación" }}
            </button>

            <button class="nav-button" type="button" @click="refreshLocations">
              Actualizar ubicaciones
            </button>
          </div>
        </section>

        <section class="stack">
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
            <article class="stat-card">
              <span>AQI global</span>
              <strong>{{ result?.aqi?.global_aqi ?? "—" }}</strong>
            </article>
            <article class="stat-card">
              <span>Categoría base</span>
              <strong>{{ result?.aqi?.category ?? "—" }}</strong>
            </article>
            <article class="stat-card">
              <span>Riesgo final</span>
              <strong>{{ result?.fuzzy?.label ?? "—" }}</strong>
            </article>
            <article class="stat-card">
              <span>Cobertura global</span>
              <strong>{{ result?.snapshot?.coverage_global ?? "—" }}</strong>
            </article>
          </section>
        </section>
      </section>

      <section v-if="result" class="panel">
        <h3>Exploración detallada</h3>
        <p class="caption">
          Usa el menú lateral para abrir cada vista en un modal. El visor muestra una sección a la vez y
          permite cambiar entre ellas sin perder la corrida actual.
        </p>
      </section>

      <section v-else class="empty-state">
        Aún no hay una corrida en memoria. Ejecuta la evaluación para poblar el panel y habilitar las vistas detalladas.
      </section>
    </main>

    <div v-if="viewerOpen && result" class="modal-overlay" @click.self="closeViewer">
      <section class="modal-card modal-card-wide">
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
            <button class="icon-button" type="button" @click="closeViewer">Cerrar</button>
          </div>
        </div>

        <div class="modal-body">
          <section v-show="currentSection === 'dashboard'" class="stack">
            <section class="panel">
              <h3>Series temporales por contaminante</h3>
              <p class="caption">
                La visualización permite inspeccionar el recorrido reciente de cada parámetro recuperado.
              </p>
              <div class="inline-field">
                <label for="seriesParameter">Parámetro</label>
                <select id="seriesParameter" v-model="selectedSeriesParameter">
                  <option v-for="item in availableSeriesParameters" :key="item" :value="item">
                    {{ item }}
                  </option>
                </select>
              </div>
            </section>

            <ChartPanel
              title="Serie temporal filtrada"
              caption="Observaciones recientes del parámetro seleccionado."
              type="line"
              :data="timeSeriesChart"
              :options="seriesLineOptions"
            />

            <ChartPanel
              title="Subíndices por contaminante"
              caption="Comparación rápida entre la base normativa y el contaminante dominante."
              type="bar"
              :data="subindicesChart"
              :options="barOptions"
            />

            <ChartPanel
              title="Resumen de evaluación"
              caption="AQI base, concurrencia, persistencia y puntuación difusa final."
              type="bar"
              :data="summaryChart"
              :options="barOptions"
            />

            <ChartPanel
              title="AQI base frente a salida final"
              caption="Comparación entre la clasificación normativa inicial y la puntuación difusa final."
              type="bar"
              :data="baseVsFinalChart"
              :options="barOptions"
            />

            <ChartPanel
              title="Variables auxiliares"
              caption="Persistencia, concurrencia y cobertura empleadas por el artefacto."
              type="bar"
              :data="auxiliaryChart"
              :options="barOptions"
            />
          </section>

          <section v-show="currentSection === 'traceability'" class="trace-grid">
            <article class="trace-box trace-box-wide">
              <h4>Ruta de decisión</h4>
              <ol class="trace-steps">
                <li>Consolidación normativa del AQI con base en EPA/AQS.</li>
                <li>Cálculo de concurrencia, persistencia y cobertura del episodio.</li>
                <li>Aplicación de la base principal de 54 reglas.</li>
                <li>Ajuste contextual por temperatura y humedad cuando existen datos.</li>
                <li>Generación de salida final, alerta y registro histórico.</li>
              </ol>
            </article>
            <article class="trace-box">
              <h4>Parámetros soportados</h4>
              <div class="tag-list">
                <span v-for="item in result.aqi.supported_parameters" :key="item" class="tag">{{ item }}</span>
              </div>
            </article>
            <article class="trace-box">
              <h4>Parámetros no soportados</h4>
              <div class="tag-list">
                <span v-for="item in result.aqi.unsupported_parameters" :key="item" class="tag">{{ item }}</span>
              </div>
            </article>
            <article class="trace-box">
              <h4>Reglas activadas</h4>
              <ul>
                <li v-for="rule in result.fuzzy.triggered_rules" :key="rule">{{ rule }}</li>
              </ul>
            </article>
            <article class="trace-box">
              <h4>Ajustes contextuales</h4>
              <ul>
                <li v-if="result.context_adjustments.length === 0">Sin ajuste contextual.</li>
                <li v-for="item in result.context_adjustments" :key="item">{{ item }}</li>
              </ul>
            </article>
            <article class="trace-box">
              <h4>Sensores disponibles</h4>
              <ul>
                <li v-if="sensors.length === 0">Sin sensores cargados.</li>
                <li v-for="item in sensors" :key="item.sensor_id">
                  {{ item.parameter }} · {{ item.units }} · sensor {{ item.sensor_id }}
                </li>
              </ul>
            </article>
          </section>

          <section v-show="currentSection === 'explainability'" class="stack">
            <ChartPanel
              title="Distribución de reglas activadas"
              caption="La gráfica refleja cuántas reglas se activaron en esta corrida."
              type="bar"
              :data="triggeredRulesChart"
              :options="barOptions"
            />

            <ChartPanel
              title="Agregación y defuzzificación"
              caption="Curva agregada del sistema difuso para la corrida actual."
              type="line"
              :data="aggregationChart"
              :options="lineOptions"
            />

            <ChartPanel
              title="Funciones de pertenencia del AQI"
              caption="Curvas base utilizadas por el motor para la variable AQI."
              type="line"
              :data="aqiMembershipChart"
              :options="lineOptionsWithLegend"
            />

            <ChartPanel
              title="Funciones de pertenencia de concurrencia"
              caption="Curvas base utilizadas para la variable de concurrencia."
              type="line"
              :data="concurrenceMembershipChart"
              :options="lineOptionsWithLegend"
            />

            <ChartPanel
              title="Funciones de pertenencia de persistencia"
              caption="Curvas base utilizadas para la variable de persistencia."
              type="line"
              :data="persistenceMembershipChart"
              :options="lineOptionsWithLegend"
            />

            <section class="panel">
              <h3>Lectura explicable del episodio</h3>
              <p class="caption">
                Dominante: <strong>{{ result.aqi.dominant_parameter || "sin dominante" }}</strong>.
                Concurrencia: <strong>{{ result.concurrence_score }}</strong>.
                Persistencia: <strong>{{ result.persistence_score }}</strong>.
                Salida final: <strong>{{ result.fuzzy.label }}</strong>.
              </p>
              <p class="caption">
                La salida principal del motor puede compararse con la salida final en la vista de evaluación
                cuando existe ajuste contextual.
              </p>
            </section>
          </section>

          <section v-show="currentSection === 'evaluation'" class="stack">
            <section class="panel">
              <h3>Resultado de evaluación</h3>
              <p class="caption">{{ result.alert.title }}</p>
              <p>{{ result.alert.message }}</p>
              <p v-if="result.alert.caution" class="status-warn">{{ result.alert.caution }}</p>
            </section>

            <ChartPanel
              title="Ajuste contextual antes y después"
              caption="Comparación entre la salida principal del motor y la salida final tras la capa contextual."
              type="bar"
              :data="contextBeforeAfterChart"
              :options="barOptions"
            />

            <section class="panel">
              <h3>Historial reciente</h3>
              <p class="caption">Corridas registradas localmente por el backend.</p>
              <div class="filter-grid">
                <div class="field">
                  <label for="historyFilter">Texto</label>
                  <input
                    id="historyFilter"
                    v-model="historyFilter"
                    type="text"
                    placeholder="Ubicación, etiqueta o AQI"
                  />
                </div>
                <div class="field">
                  <label for="historyDate">Fecha</label>
                  <input id="historyDate" v-model="historyDateFilter" type="date" />
                </div>
                <div class="field">
                  <label for="historyParameter">Parámetro dominante</label>
                  <select id="historyParameter" v-model="historyParameterFilter">
                    <option value="">Todos</option>
                    <option v-for="item in historyParameters" :key="item" :value="item">
                      {{ item }}
                    </option>
                  </select>
                </div>
              </div>
              <ul class="history-list">
                <li v-if="filteredHistoryItems.length === 0">Sin corridas registradas.</li>
                <li v-for="item in filteredHistoryItems" :key="item.recorded_at">
                  <button
                    class="history-button"
                    :class="{ active: selectedHistoryItem?.recorded_at === item.recorded_at }"
                    type="button"
                    @click="selectedHistoryItem = item"
                  >
                    <strong>{{ item.summary.location_name || "sin ubicación" }}</strong>
                    <span>{{ item.recorded_at }}</span>
                    <span>
                      AQI {{ item.summary.aqi_global ?? "NR" }} · {{ item.summary.fuzzy_label }} ·
                      {{ item.summary.dominant_parameter || "sin dominante" }}
                    </span>
                  </button>
                </li>
              </ul>
            </section>

            <ChartPanel
              v-if="selectedHistoryItem"
              title="Comparación con corrida histórica"
              caption="Contrasta la corrida actual con la corrida histórica seleccionada."
              type="bar"
              :data="historyComparisonChart"
              :options="barOptions"
            />
          </section>
        </div>
      </section>
    </div>

    <div v-if="modalState.open" class="modal-overlay" @click.self="closeModal">
      <section class="modal-card">
        <div class="modal-head">
          <div>
            <h3>{{ modalState.title }}</h3>
            <p class="caption" v-if="modalState.caption">{{ modalState.caption }}</p>
          </div>
          <button class="icon-button" type="button" @click="closeModal">Cerrar</button>
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
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from "vue";
import ChartPanel from "./components/ChartPanel.vue";
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
const submitting = ref(false);
const result = ref(null);
const locations = ref([]);
const sensors = ref([]);
const historyItems = ref([]);
const historyFilter = ref("");
const historyDateFilter = ref("");
const historyParameterFilter = ref("");
const selectedHistoryItem = ref(null);
const selectedLocationPreset = ref("");
const scenarios = ref([]);
const viewerOpen = ref(false);
const modalState = reactive({
  open: false,
  title: "",
  caption: "",
  mode: "list",
  items: [],
});

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
    y: { beginAtZero: true },
  },
};

const lineOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
  },
  scales: {
    x: { type: "linear" },
    y: { beginAtZero: true, max: 1.05 },
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
    y: { beginAtZero: true },
  },
};

const palette = ["#1d6fd8", "#d68716", "#ca4b34", "#1d8b5c", "#6a4bcf", "#15304b"];

const currentRunSummary = computed(() => ({
  source: form.mode === "mock" ? "Escenario controlado" : "OpenAQ",
  entry:
    form.mode === "mock"
      ? scenarios.value.find((item) => item.scenario_id === form.scenario_id)?.name || form.scenario_id
      : result.value?.snapshot?.location_name || form.location_id || "sin ubicación",
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
        body: "La lista de reglas activadas y los ajustes contextuales permiten justificar por qué la salida final se mantuvo o cambió frente a la clasificación base.",
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
  return {
    labels,
    datasets: [
      {
        label: "Subíndice",
        data: labels.map((label) => result.value.aqi.subindices[label]),
        backgroundColor: "#1d6fd8",
        borderRadius: 8,
      },
    ],
  };
});

const summaryChart = computed(() => ({
  labels: ["AQI base", "Concurrencia", "Persistencia", "Puntuación difusa"],
  datasets: [
    {
      data: [
        result.value?.aqi?.global_aqi || 0,
        result.value?.concurrence_score || 0,
        result.value?.persistence_score || 0,
        result.value?.fuzzy?.score || 0,
      ],
      backgroundColor: ["#1d6fd8", "#d68716", "#ca4b34", "#1d8b5c"],
      borderRadius: 8,
    },
  ],
}));

const baseVsFinalChart = computed(() => ({
  labels: ["AQI base", "Puntuación difusa"],
  datasets: [
    {
      data: [result.value?.aqi?.global_aqi || 0, result.value?.fuzzy?.score || 0],
      backgroundColor: ["#1d6fd8", "#1d8b5c"],
      borderRadius: 8,
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
      backgroundColor: ["#d68716", "#ca4b34", "#1d8b5c"],
      borderRadius: 8,
    },
  ],
}));

const triggeredRulesChart = computed(() => ({
  labels: (result.value?.fuzzy?.triggered_rules || []).length
    ? result.value.fuzzy.triggered_rules
    : ["sin reglas"],
  datasets: [
    {
      data: (result.value?.fuzzy?.triggered_rules || []).length
        ? result.value.fuzzy.triggered_rules.map(() => 1)
        : [0],
      backgroundColor: "#15304b",
      borderRadius: 8,
    },
  ],
}));

const availableSeriesParameters = computed(() => Object.keys(result.value?.snapshot?.series || {}));

const timeSeriesChart = computed(() => {
  const observations = result.value?.snapshot?.series?.[selectedSeriesParameter.value]?.observations || [];
  return {
    labels: observations.map((item) => item.datetime_to),
    datasets: [
      {
        label: selectedSeriesParameter.value,
        data: observations.map((item) => item.value),
        borderColor: "#1d6fd8",
        backgroundColor: "rgba(29, 111, 216, 0.18)",
        fill: true,
        tension: 0.22,
      },
    ],
  };
});

const aggregationChart = computed(() => {
  const points = result.value?.explainability?.layer_outputs?.inferencia_difusa_principal?.aggregation_samples || [];
  return {
    datasets: [
      {
        label: "Agregación difusa",
        data: points.map((item) => ({ x: item.x, y: item.membership })),
        borderColor: "#15304b",
        backgroundColor: "rgba(21, 48, 75, 0.18)",
        fill: true,
        tension: 0.25,
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
        backgroundColor: ["#d68716", "#1d8b5c"],
        borderRadius: 8,
      },
    ],
  };
});

const filteredHistoryItems = computed(() => {
  const term = historyFilter.value.trim().toLowerCase();
  return historyItems.value.filter((item) => {
    const haystack = [
      item.recorded_at,
      item.summary.location_name,
      item.summary.fuzzy_label,
      item.summary.dominant_parameter,
      String(item.summary.aqi_global ?? ""),
    ]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();
    const matchesText = !term || haystack.includes(term);
    const matchesDate =
      !historyDateFilter.value || String(item.recorded_at || "").startsWith(historyDateFilter.value);
    const matchesParameter =
      !historyParameterFilter.value ||
      String(item.summary.dominant_parameter || "") === historyParameterFilter.value;
    return matchesText && matchesDate && matchesParameter;
  });
});

const historyParameters = computed(() => {
  return [...new Set(historyItems.value.map((item) => item.summary.dominant_parameter).filter(Boolean))];
});

const historyComparisonChart = computed(() => {
  const current = result.value;
  const previous = selectedHistoryItem.value;
  return {
    labels: ["AQI", "Cobertura", "Puntuación difusa"],
    datasets: [
      {
        label: "Actual",
        data: [
          current?.aqi?.global_aqi || 0,
          current?.snapshot?.coverage_global || 0,
          current?.fuzzy?.score || 0,
        ],
        backgroundColor: "#1d6fd8",
        borderRadius: 8,
      },
      {
        label: "Histórica",
        data: [
          previous?.summary?.aqi_global || 0,
          previous?.summary?.coverage_global || 0,
          previous?.summary?.fuzzy_score || 0,
        ],
        backgroundColor: "#d68716",
        borderRadius: 8,
      },
    ],
  };
});

function buildMembershipChart(curves) {
  const entries = Object.entries(curves || {});
  return {
    datasets: entries.map(([term, points], index) => ({
      label: term,
      data: points.map((item) => ({ x: item.x, y: item.membership })),
      borderColor: palette[index % palette.length],
      backgroundColor: "transparent",
      tension: 0.22,
    })),
  };
}

const aqiMembershipChart = computed(() => buildMembershipChart(metadata.model.membership_curves?.aqi));
const concurrenceMembershipChart = computed(() => buildMembershipChart(metadata.model.membership_curves?.concurrence));
const persistenceMembershipChart = computed(() => buildMembershipChart(metadata.model.membership_curves?.persistence));

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

function applySelectedLocation() {
  if (!selectedLocationPreset.value) {
    return;
  }
  form.location_id = selectedLocationPreset.value;
  loadSensors(Number(selectedLocationPreset.value));
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

async function loadHealth() {
  try {
    await checkHealth();
    healthMessage.value = "Servicio disponible.";
    healthStatusClass.value = "status-ok";
  } catch (error) {
    healthMessage.value = "Backend no disponible.";
    healthStatusClass.value = "status-danger";
  }
}

async function runEvaluation() {
  submitting.value = true;
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
  } finally {
    submitting.value = false;
  }
}

onMounted(async () => {
  await Promise.all([loadMetadata(), loadHealth(), refreshLocations(), refreshHistory(), refreshScenarios()]);
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
</script>
