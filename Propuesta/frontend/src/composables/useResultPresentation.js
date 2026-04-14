import { computed } from "vue";

export function useResultPresentation({
  currentSection,
  form,
  metadata,
  result,
  scenarios,
  sections,
  selectedLocationName,
}) {
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
  const principalTrace = computed(
    () => result.value?.explainability?.layer_outputs?.inferencia_difusa_principal || {},
  );
  const contextTrace = computed(
    () => result.value?.explainability?.layer_outputs?.ajuste_contextual || {},
  );
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

  return {
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
    selectedScenarioName,
    statCards,
  };
}
