import { computed, reactive, ref } from "vue";

import {
  checkHealth,
  evaluateModule,
  fetchHistory,
  fetchLocationSensors,
  fetchLocations,
  fetchMetadata,
  fetchScenarios,
} from "../services/api";

export function useWorkspaceData() {
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:18010";
  const healthMessage = ref("Verificando servicio...");
  const healthStatusClass = ref("");
  const lastError = ref("");
  const submitting = ref(false);
  const result = ref(null);
  const locations = ref([]);
  const sensors = ref([]);
  const historyItems = ref([]);
  const scenarios = ref([]);

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

  const isBackendReady = computed(() => healthStatusClass.value === "status-ok");
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
      await refreshHistory();
      if (payload.location_id) {
        await loadSensors(payload.location_id);
      }
    } catch (error) {
      const detail = error?.response?.data?.error || error.message;
      healthMessage.value = detail;
      healthStatusClass.value = "status-danger";
      lastError.value = detail;
      throw error;
    } finally {
      submitting.value = false;
    }
  }

  async function initializeWorkspace() {
    await Promise.all([loadMetadata(), loadHealth(), refreshLocations(), refreshHistory(), refreshScenarios()]);
  }

  return {
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
    loadHealth,
    loadMetadata,
    loadSensors,
    locations,
    metadata,
    refreshHistory,
    refreshLocations,
    refreshScenarios,
    result,
    runEvaluation,
    scenarios,
    sensors,
    submitting,
  };
}
