import { nextTick, ref } from "vue";

function parseBooleanParam(value) {
  return value === "1" || value === "true" || value === "yes";
}

export function useCaptureMode({
  currentSection,
  form,
  metadata,
  result,
  runEvaluation,
  sections,
  selectedSeriesParameter,
  viewerOpen,
}) {
  const captureMode = ref(false);

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
      locationId,
      mode,
      scenarioId,
      section,
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

  function clearCaptureMode() {
    if (typeof document !== "undefined") {
      delete document.body.dataset.captureMode;
    }
  }

  return {
    applyCaptureConfig,
    captureMode,
    clearCaptureMode,
    readCaptureConfig,
  };
}
