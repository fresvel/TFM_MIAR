<template>
  <section class="trace-grid">
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
    <article class="trace-box trace-box-wide">
      <h4>Entradas reales del motor y salidas</h4>
      <div class="trace-metric-grid">
        <div class="trace-metric">
          <div class="trace-metric-head">
            <span class="trace-metric-label">AQI global</span>
            <div class="trace-info-wrap">
              <button class="trace-info-button" type="button" aria-label="Escala AQI">i</button>
              <span class="trace-tooltip">{{ metricHelp.aqi }}</span>
            </div>
          </div>
          <strong>{{ result.aqi.global_aqi ?? "sin dato" }}</strong>
          <span class="trace-metric-note">Dominante: {{ result.aqi.dominant_parameter || "sin dominante" }}</span>
        </div>
        <div class="trace-metric">
          <div class="trace-metric-head">
            <span class="trace-metric-label">Concurrencia</span>
            <div class="trace-info-wrap">
              <button class="trace-info-button" type="button" aria-label="Escala concurrencia">i</button>
              <span class="trace-tooltip">{{ metricHelp.concurrence }}</span>
            </div>
          </div>
          <strong>{{ Number(result.concurrence_score || 0).toFixed(2) }}</strong>
          <span class="trace-metric-note">Entrada auxiliar multicontaminante</span>
        </div>
        <div class="trace-metric">
          <div class="trace-metric-head">
            <span class="trace-metric-label">Persistencia</span>
            <div class="trace-info-wrap">
              <button class="trace-info-button" type="button" aria-label="Escala persistencia">i</button>
              <span class="trace-tooltip">{{ metricHelp.persistence }}</span>
            </div>
          </div>
          <strong>{{ Number(result.persistence_score || 0).toFixed(2) }}</strong>
          <span class="trace-metric-note">Continuidad temporal del AQI base</span>
        </div>
        <div class="trace-metric">
          <div class="trace-metric-head">
            <span class="trace-metric-label">Salida principal</span>
            <div class="trace-info-wrap">
              <button class="trace-info-button" type="button" aria-label="Escala salida principal">i</button>
              <span class="trace-tooltip">{{ metricHelp.aqi }}</span>
            </div>
          </div>
          <strong>{{ Number(principalScore).toFixed(2) }}</strong>
          <span class="trace-metric-note">{{ principalLabel }}</span>
        </div>
        <div class="trace-metric">
          <div class="trace-metric-head">
            <span class="trace-metric-label">Salida final</span>
            <div class="trace-info-wrap">
              <button class="trace-info-button" type="button" aria-label="Escala salida final">i</button>
              <span class="trace-tooltip">{{ metricHelp.aqi }}</span>
            </div>
          </div>
          <strong>{{ Number(result.fuzzy.score || 0).toFixed(2) }}</strong>
          <span class="trace-metric-note">{{ finalLabel }}</span>
        </div>
        <div class="trace-metric">
          <div class="trace-metric-head">
            <span class="trace-metric-label">Cobertura global</span>
            <div class="trace-info-wrap">
              <button class="trace-info-button" type="button" aria-label="Escala cobertura">i</button>
              <span class="trace-tooltip">{{ metricHelp.coverage }}</span>
            </div>
          </div>
          <strong>{{ Number(result.snapshot.coverage_global || 0).toFixed(1) }}%</strong>
          <span class="trace-metric-note">Calidad de dato, fuera de la malla difusa</span>
        </div>
      </div>
      <div class="trace-output-summary" :class="finalSummaryClass">
        <span class="trace-metric-label">Explicación de salida final</span>
        <p class="trace-metric-note">
          La inferencia principal produjo <strong>{{ Number(principalScore).toFixed(2) }}</strong>
          ({{ principalLabel }}). La capa contextual dejó la salida en
          <strong>{{ Number(result.fuzzy.score || 0).toFixed(2) }}</strong>
          ({{ finalLabel }}) {{ finalExplanationSuffix }}.
        </p>
      </div>
    </article>
    <article class="trace-box">
      <h4>Parámetros soportados</h4>
      <div class="tag-list">
        <span v-for="item in result.aqi.supported_parameters" :key="item" class="tag">{{ item }}</span>
      </div>
    </article>
    <article class="trace-box">
      <h4>Parámetros sin subíndice AQI válido</h4>
      <div class="tag-list">
        <span
          v-for="item in normativeUnsupportedParameters"
          :key="item"
          class="tag"
        >
          {{ item }}
        </span>
        <span v-if="normativeUnsupportedParameters.length === 0" class="tag">
          ninguno
        </span>
      </div>
    </article>
    <article class="trace-box">
      <h4>Reglas activadas</h4>
      <div v-if="activatedRuleDetails.length === 0" class="trace-empty">
        Sin reglas activadas.
      </div>
      <div v-else class="trace-rule-grid">
        <div v-for="rule in activatedRuleDetails" :key="rule.name" class="trace-rule-card">
          <span class="trace-metric-label">Regla</span>
          <strong>{{ rule.name }}</strong>
          <span class="trace-metric-note">{{ describeMainRule(rule) }}</span>
          <div class="trace-rule-meta">
            <span class="tag tag-muted">Fuerza {{ rule.strengthLabel }}</span>
            <span class="tag tag-success">Salida {{ rule.outputLabel }}</span>
          </div>
        </div>
      </div>
    </article>
    <article class="trace-box">
      <h4>Ajustes contextuales</h4>
      <div class="tag-list trace-context-tags">
        <span
          v-for="item in contextAvailabilityTags"
          :key="item.label"
          class="tag"
          :class="item.stateClass"
        >
          {{ item.label }}
        </span>
      </div>
      <div class="trace-context-grid">
        <div class="trace-context-item">
          <span class="trace-metric-label">Temperatura</span>
          <strong>{{ contextTemperatureLabel }}</strong>
          <span class="trace-metric-note">Término: {{ contextTemperatureTerm }}</span>
        </div>
        <div class="trace-context-item">
          <span class="trace-metric-label">Humedad</span>
          <strong>{{ contextHumidityLabel }}</strong>
          <span class="trace-metric-note">Término: {{ contextHumidityTerm }}</span>
        </div>
        <div class="trace-context-item">
          <span class="trace-metric-label">Regla contextual</span>
          <strong>{{ contextRuleLabel }}</strong>
          <span class="trace-metric-note">Fuerza: {{ contextStrengthLabel }}</span>
          <span class="trace-metric-note">Escalado: {{ contextEscalationLabel }}</span>
          <span class="trace-metric-note">{{ contextRuleDescription }}</span>
        </div>
        <div class="trace-context-item">
          <span class="trace-metric-label">Estado</span>
          <strong>{{ contextStatusLabel }}</strong>
          <span class="trace-metric-note">{{ contextReasonLabel }}</span>
        </div>
      </div>
      <div v-if="result.context_adjustments.length === 0" class="trace-empty">
        Sin ajuste contextual aplicado.
      </div>
    </article>
    <article v-if="showSensors" class="trace-box">
      <h4>Sensores disponibles</h4>
      <ul>
        <li v-if="sensors.length === 0">Sin sensores cargados.</li>
        <li v-for="item in sensors" :key="item.sensor_id">
          {{ item.parameter }} · {{ item.units }} · sensor {{ item.sensor_id }}
        </li>
      </ul>
    </article>
  </section>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  activatedRuleDetails: { type: Array, required: true },
  result: { type: Object, required: true },
  sensors: { type: Array, required: true },
});

const principalLayer = computed(
  () => props.result.explainability?.layer_outputs?.inferencia_difusa_principal || {},
);
const contextLayer = computed(
  () => props.result.explainability?.layer_outputs?.ajuste_contextual || {},
);
const normativeUnsupportedParameters = computed(() =>
  (props.result.aqi?.unsupported_parameters || []).filter(
    (item) => !["temperature", "humidity"].includes(String(item)),
  ),
);

const principalScore = computed(() => principalLayer.value.score || 0);
const principalLabel = computed(() =>
  String(principalLayer.value.label || "sin etiqueta").replaceAll("_", " "),
);
const finalLabel = computed(() =>
  String(props.result.fuzzy?.label || "sin etiqueta").replaceAll("_", " "),
);
const metricHelp = {
  aqi: "Escala AQI 0-500. Categorías: good 0-50, moderate 51-100, unhealthy sensitive groups 101-150, unhealthy 151-200, very unhealthy 201-300, hazardous 301-500.",
  concurrence:
    "Escala 0-100. Rangos difusos solapados: low ~ 0-45, medium ~ 35-75, high ~ 65-100. Resume cuántos contaminantes adicionales quedan cerca del dominante.",
  persistence:
    "Escala 0-100. Rangos difusos solapados: low ~ 0-40, medium ~ 30-75, high ~ 65-100. Resume cuánto se sostiene el AQI base en la historia reciente.",
  coverage:
    "Escala 0-100%. Indica completitud de datos para la corrida. No entra a la malla difusa principal. El umbral operativo mínimo del sistema es 80%.",
};
const showSensors = computed(() => props.result.snapshot?.source === "openaq");
const contextTemperatureLabel = computed(() =>
  contextLayer.value.temperature == null ? "sin dato" : `${contextLayer.value.temperature}`,
);
const contextHumidityLabel = computed(() =>
  contextLayer.value.humidity == null ? "sin dato" : `${contextLayer.value.humidity}`,
);
const contextTemperatureTerm = computed(() => contextLayer.value.temperature_term || "sin término");
const contextHumidityTerm = computed(() => contextLayer.value.humidity_term || "sin término");
const contextRuleLabel = computed(() => contextLayer.value.rule || "sin regla contextual");
const contextStrengthLabel = computed(() =>
  contextLayer.value.rule ? "1.00 (activación crisp)" : "0.00",
);
const contextEscalationLabel = computed(() => `${contextLayer.value.escalation || 0} nivel(es)`);
const contextAvailabilityTags = computed(() => [
  {
    label: contextLayer.value.temperature == null ? "Temperatura ausente" : "Temperatura disponible",
    stateClass: contextLayer.value.temperature == null ? "tag-danger" : "tag-success",
  },
  {
    label: contextLayer.value.humidity == null ? "Humedad ausente" : "Humedad disponible",
    stateClass: contextLayer.value.humidity == null ? "tag-danger" : "tag-success",
  },
  {
    label: contextLayer.value.rule ? `Regla evaluada: ${contextLayer.value.rule}` : "Sin regla contextual",
    stateClass: contextLayer.value.applied ? "tag-success" : "tag-muted",
  },
]);
const contextStatusLabel = computed(() =>
  contextLayer.value.applied ? "aplicado" : "sin aplicación",
);
const contextRuleDescription = computed(() => {
  if (!contextLayer.value.rule) {
    return "La capa contextual no pudo evaluarse por falta de variables ambientales.";
  }

  const descriptions = {
    CTX_low_low: "Temperatura baja y humedad baja: la capa contextual no escala la salida principal.",
    CTX_low_medium: "Temperatura baja y humedad media: la capa contextual no escala la salida principal.",
    CTX_low_high: "Temperatura baja y humedad alta: la capa contextual no escala la salida principal.",
    CTX_normal_low: "Temperatura normal y humedad baja: la capa contextual no escala la salida principal.",
    CTX_normal_medium: "Temperatura normal y humedad media: la capa contextual no escala la salida principal.",
    CTX_normal_high:
      "Temperatura normal y humedad alta: la capa contextual propone escalar una categoría.",
    CTX_high_low: "Temperatura alta y humedad baja: la capa contextual no escala la salida principal.",
    CTX_high_medium:
      "Temperatura alta y humedad media: la capa contextual propone escalar una categoría.",
    CTX_high_high:
      "Temperatura alta y humedad alta: la capa contextual propone escalar una categoría.",
  };
  return descriptions[contextLayer.value.rule] || "Regla contextual evaluada sin descripción registrada.";
});
const contextReasonLabel = computed(() => {
  const reason = String(contextLayer.value.reason || "sin_detalle");
  const labels = {
    sin_datos_contextuales: "No había temperatura y humedad válidas para evaluar la capa contextual.",
    regla_contextual_sin_escalado: "La combinación de temperatura y humedad existe, pero la regla contextual no escala.",
    escalado_bloqueado_por_umbral_particulado:
      "La regla contextual escala, pero el guardarraíl particulado bloquea el ajuste cuando PM y AQI siguen bajos.",
    escalado_contextual_aplicado: "La regla contextual elevó la salida final respecto de la salida principal.",
  };
  return labels[reason] || reason.replaceAll("_", " ");
});
const finalSummaryClass = computed(() => {
  const label = String(props.result.fuzzy?.label || "");
  const mapping = {
    good: "trace-output-good",
    moderate: "trace-output-moderate",
    unhealthy_sensitive_groups: "trace-output-usg",
    unhealthy: "trace-output-unhealthy",
    very_unhealthy: "trace-output-very-unhealthy",
    hazardous: "trace-output-hazardous",
  };
  return mapping[label] || "";
});
const finalExplanationSuffix = computed(() => {
  if (contextLayer.value.applied) {
    return `porque la regla contextual ${contextLayer.value.rule} aplicó un escalado de ${contextLayer.value.escalation || 0} nivel(es)`;
  }
  if (contextLayer.value.rule) {
    return `porque la regla contextual ${contextLayer.value.rule} no modificó la salida principal`;
  }
  return "porque no hubo datos contextuales válidos para evaluar esa capa";
});

function humanizeTerm(value) {
  return String(value || "sin término").replaceAll("_", " ");
}

function describeMainRule(rule) {
  return `Si AQI es ${humanizeTerm(rule.aqi_term)}, concurrencia es ${humanizeTerm(
    rule.concurrence_term,
  )} y persistencia es ${humanizeTerm(rule.persistence_term)}, entonces la salida es ${humanizeTerm(
    rule.output_term,
  )}.`;
}
</script>

<style scoped>
.trace-metric-grid {
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.trace-metric {
  border: 1px solid rgba(124, 145, 159, 0.2);
  border-radius: 8px;
  padding: 10px;
  background: rgba(8, 15, 23, 0.04);
}

.trace-metric-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.trace-info-wrap {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.trace-context-grid {
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin-bottom: 10px;
}

.trace-context-tags {
  margin-bottom: 10px;
}

.tag-success {
  background: rgba(70, 179, 77, 0.12);
  border-color: rgba(70, 179, 77, 0.35);
  color: #2c6f31;
}

.tag-danger {
  background: rgba(209, 94, 67, 0.12);
  border-color: rgba(209, 94, 67, 0.35);
  color: #8d3726;
}

.tag-muted {
  background: rgba(98, 112, 121, 0.12);
  border-color: rgba(98, 112, 121, 0.28);
  color: #56626a;
}

.trace-context-item {
  border: 1px solid rgba(124, 145, 159, 0.2);
  border-radius: 8px;
  padding: 10px;
  background: rgba(8, 15, 23, 0.04);
}

.trace-rule-grid {
  display: grid;
  gap: 10px;
}

.trace-rule-card {
  border: 1px solid rgba(124, 145, 159, 0.2);
  border-radius: 8px;
  padding: 10px;
  background: rgba(8, 15, 23, 0.04);
}

.trace-rule-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.trace-empty {
  color: #627079;
  font-size: 0.95rem;
}

.trace-output-summary {
  margin-top: 10px;
  border: 1px solid rgba(124, 145, 159, 0.2);
  border-radius: 8px;
  padding: 10px;
  background: rgba(8, 15, 23, 0.03);
}

.trace-output-summary p {
  margin: 0;
}

.trace-output-good {
  background: rgba(70, 179, 77, 0.1);
  border-color: rgba(70, 179, 77, 0.28);
}

.trace-output-moderate {
  background: rgba(211, 139, 30, 0.1);
  border-color: rgba(211, 139, 30, 0.28);
}

.trace-output-usg {
  background: rgba(227, 164, 58, 0.12);
  border-color: rgba(227, 164, 58, 0.34);
}

.trace-output-unhealthy {
  background: rgba(209, 94, 67, 0.1);
  border-color: rgba(209, 94, 67, 0.3);
}

.trace-output-very-unhealthy {
  background: rgba(141, 55, 38, 0.12);
  border-color: rgba(141, 55, 38, 0.34);
}

.trace-output-hazardous {
  background: rgba(32, 39, 56, 0.12);
  border-color: rgba(32, 39, 56, 0.34);
}

.trace-metric strong {
  display: block;
  font-size: 1.2rem;
  line-height: 1.2;
  margin-bottom: 4px;
}

.trace-metric-label,
.trace-metric-note {
  display: block;
}

.trace-metric-label {
  margin-bottom: 6px;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: #627079;
}

.trace-info-button {
  width: 20px;
  height: 20px;
  border-radius: 6px;
  border: 1px solid rgba(124, 145, 159, 0.28);
  background: rgba(8, 15, 23, 0.04);
  color: #627079;
  font-size: 0.78rem;
  font-weight: 700;
  line-height: 1;
  cursor: help;
  flex-shrink: 0;
}

.trace-tooltip {
  position: absolute;
  right: 0;
  top: calc(100% + 8px);
  z-index: 4;
  width: 260px;
  padding: 10px 11px;
  border-radius: 8px;
  border: 1px solid rgba(124, 145, 159, 0.28);
  background: #ffffff;
  color: #243039;
  font-size: 0.95rem;
  line-height: 1.45;
  box-shadow: 0 12px 24px rgba(16, 24, 32, 0.12);
  opacity: 0;
  pointer-events: none;
  transform: translateY(-4px);
  transition: opacity 0.16s ease, transform 0.16s ease;
}

.trace-info-wrap:hover .trace-tooltip,
.trace-info-wrap:focus-within .trace-tooltip {
  opacity: 1;
  transform: translateY(0);
}

.trace-metric-note {
  color: #627079;
  font-size: 0.88rem;
}

@media (max-width: 980px) {
  .trace-metric-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 680px) {
  .trace-metric-grid {
    grid-template-columns: 1fr;
  }

  .trace-context-grid {
    grid-template-columns: 1fr;
  }
}
</style>
