<template>
  <section class="stack">
    <section class="panel">
      <h3>Lectura explicable del episodio</h3>
      <p class="caption">
        Esta vista describe la inferencia difusa principal. Las curvas muestran la base del motor y
        la línea punteada marca el valor real de la corrida.
      </p>
      <div class="explain-grid">
        <div class="explain-card">
          <span class="explain-label">AQI de entrada</span>
          <strong>{{ principalTrace.inputs?.aqi ?? 0 }}</strong>
          <span class="caption">{{ explainMemberships("aqi") }}</span>
        </div>
        <div class="explain-card">
          <span class="explain-label">Concurrencia</span>
          <strong>{{ result.concurrence_score }}</strong>
          <span class="caption">{{ explainMemberships("concurrence") }}</span>
        </div>
        <div class="explain-card">
          <span class="explain-label">Persistencia</span>
          <strong>{{ result.persistence_score }}</strong>
          <span class="caption">{{ explainMemberships("persistence") }}</span>
        </div>
        <div class="explain-card explain-card-wide">
          <span class="explain-label">Salida principal y salida final</span>
          <strong>{{ principalTrace.label || "sin etiqueta" }} → {{ result.fuzzy.label }}</strong>
          <span class="caption">
            Score principal: {{ principalTrace.score ?? 0 }}. Score final: {{ result.fuzzy.score }}.
            La salida final solo cambia si la capa contextual modifica la salida principal.
          </span>
        </div>
      </div>
    </section>

    <section class="panel">
      <h3>Capa contextual basada en reglas</h3>
      <p class="caption">
        Esta capa no es difusa. Clasifica temperatura y humedad con cortes crisp, evalúa una matriz
        de 9 reglas y luego decide si escala o no la salida principal.
      </p>
      <div class="context-grid">
        <div class="context-card">
          <span class="explain-label">Temperatura</span>
          <strong>{{ contextTrace.temperature ?? "sin dato" }}</strong>
          <span class="caption">Término activo: {{ contextTrace.temperature_term || "sin término" }}</span>
          <div class="context-band">
            <div class="context-band-segment">low</div>
            <div class="context-band-segment">normal</div>
            <div class="context-band-segment">high</div>
            <div
              v-if="hasTemperature"
              class="context-band-marker"
              :style="{ left: `${temperatureMarker}%` }"
            >
              <span></span>
            </div>
          </div>
          <p class="caption">Cortes actuales: `low <= 10`, `normal < 30`, `high >= 30`.</p>
        </div>

        <div class="context-card">
          <span class="explain-label">Humedad</span>
          <strong>{{ contextTrace.humidity ?? "sin dato" }}</strong>
          <span class="caption">Término activo: {{ contextTrace.humidity_term || "sin término" }}</span>
          <div class="context-band">
            <div class="context-band-segment">low</div>
            <div class="context-band-segment">medium</div>
            <div class="context-band-segment">high</div>
            <div
              v-if="hasHumidity"
              class="context-band-marker"
              :style="{ left: `${humidityMarker}%` }"
            >
              <span></span>
            </div>
          </div>
          <p class="caption">Cortes actuales: `low < 40`, `medium < 70`, `high >= 70`.</p>
        </div>

        <div class="context-card context-card-wide">
          <span class="explain-label">Matriz contextual 3 × 3</span>
          <div class="context-matrix">
            <div class="context-corner"></div>
            <div class="context-header" v-for="humidity in humidityTerms" :key="`h-${humidity}`">
              {{ humidity }}
            </div>
            <template v-for="temperature in temperatureTerms" :key="`row-${temperature}`">
              <div class="context-header">{{ temperature }}</div>
              <div
                v-for="humidity in humidityTerms"
                :key="`${temperature}-${humidity}`"
                class="context-cell"
                :class="contextCellClass(temperature, humidity)"
              >
                <strong>CTX_{{ temperature }}_{{ humidity }}</strong>
                <span>{{ contextMatrix[temperature][humidity] ? "escala +1" : "sin escalado" }}</span>
              </div>
            </template>
          </div>
          <p class="caption">
            La celda resaltada corresponde a la combinación actual evaluada por la capa contextual.
          </p>
        </div>

        <div class="context-card context-card-wide">
          <span class="explain-label">Guardarraíl particulado y efecto final</span>
          <div class="context-guard-grid">
            <div class="explain-card">
              <span class="explain-label">Regla evaluada</span>
              <strong>{{ contextTrace.rule || "sin regla contextual" }}</strong>
              <span class="caption">Escalado propuesto: {{ contextTrace.escalation || 0 }} nivel(es).</span>
            </div>
            <div class="explain-card">
              <span class="explain-label">Particulado de control</span>
              <strong>{{ contextTrace.particulate_index ?? 0 }}</strong>
              <span class="caption">Máximo entre `pm25` y `pm10` para decidir si se permite el ajuste.</span>
            </div>
            <div class="explain-card">
              <span class="explain-label">Resultado contextual</span>
              <strong>{{ contextTrace.applied ? "aplicado" : "no aplicado" }}</strong>
              <span class="caption">{{ contextReasonLabel }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <ChartPanel
      title="Reglas activadas y fuerza de disparo"
      caption="Cada barra representa una regla de la inferencia principal que se activó y su fuerza de activación."
      type="bar"
      :data="triggeredRulesChart"
      :options="barOptions"
    />

    <ChartPanel
      title="Agregación difusa y score principal"
      caption="La curva muestra la agregación de salidas recortadas y el punto marca el score principal antes del ajuste contextual."
      type="line"
      :data="aggregationChart"
      :options="lineOptions"
    />

    <ChartPanel
      title="Funciones de pertenencia del AQI"
      caption="Curvas base de la variable AQI. La línea punteada indica el AQI real usado por el motor."
      type="line"
      :data="aqiMembershipChart"
      :options="lineOptionsWithLegend"
    />

    <ChartPanel
      title="Funciones de pertenencia de concurrencia"
      caption="Curvas base de concurrencia. La línea punteada indica el valor de concurrencia de esta corrida."
      type="line"
      :data="concurrenceMembershipChart"
      :options="lineOptionsWithLegend"
    />

    <ChartPanel
      title="Funciones de pertenencia de persistencia"
      caption="Curvas base de persistencia. La línea punteada indica el valor de persistencia de esta corrida."
      type="line"
      :data="persistenceMembershipChart"
      :options="lineOptionsWithLegend"
    />
  </section>
</template>

<script setup>
import { computed } from "vue";

import ChartPanel from "./ChartPanel.vue";

const props = defineProps({
  aggregationChart: { type: Object, required: true },
  aqiMembershipChart: { type: Object, required: true },
  barOptions: { type: Object, required: true },
  concurrenceMembershipChart: { type: Object, required: true },
  contextTrace: { type: Object, required: true },
  lineOptions: { type: Object, required: true },
  lineOptionsWithLegend: { type: Object, required: true },
  persistenceMembershipChart: { type: Object, required: true },
  principalTrace: { type: Object, required: true },
  result: { type: Object, required: true },
  triggeredRulesChart: { type: Object, required: true },
});

const temperatureTerms = ["low", "normal", "high"];
const humidityTerms = ["low", "medium", "high"];
const contextMatrix = {
  low: { low: 0, medium: 0, high: 0 },
  normal: { low: 0, medium: 0, high: 1 },
  high: { low: 0, medium: 1, high: 1 },
};

function explainMemberships(kind) {
  const memberships = props.principalTrace.memberships?.[kind] || {};
  const active = Object.entries(memberships)
    .filter(([, value]) => Number(value) > 0)
    .map(([term, value]) => `${term}: ${Number(value).toFixed(2)}`);
  return active.length ? `Pertenencias activas: ${active.join(" · ")}` : "Sin pertenencias activas.";
}

function clampPercent(value, max) {
  return Math.max(0, Math.min(100, (Number(value) / max) * 100));
}

const hasTemperature = computed(() => props.contextTrace.temperature != null);
const hasHumidity = computed(() => props.contextTrace.humidity != null);
const temperatureMarker = computed(() => clampPercent(props.contextTrace.temperature ?? 0, 45));
const humidityMarker = computed(() => clampPercent(props.contextTrace.humidity ?? 0, 100));
const contextReasonLabel = computed(() =>
  ({
    sin_datos_contextuales: "No había temperatura y humedad válidas para evaluar la capa contextual.",
    regla_contextual_sin_escalado: "La regla existe, pero su salida es 0 y no modifica la salida principal.",
    escalado_bloqueado_por_umbral_particulado:
      "La regla propone escalado, pero el guardarraíl particulado bloquea el ajuste porque PM y AQI aún no justifican esa subida.",
    escalado_contextual_aplicado: "La regla contextual se aplicó y elevó la salida final respecto de la principal.",
  }[props.contextTrace.reason] || "Sin detalle contextual.")
);

function contextCellClass(temperature, humidity) {
  return {
    "context-cell-active":
      props.contextTrace.temperature_term === temperature && props.contextTrace.humidity_term === humidity,
    "context-cell-escalates": contextMatrix[temperature][humidity] === 1,
  };
}
</script>

<style scoped>
.explain-grid {
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  margin-top: 10px;
}

.explain-card {
  border: 1px solid rgba(124, 145, 159, 0.2);
  border-radius: 8px;
  padding: 10px;
  background: rgba(8, 15, 23, 0.04);
}

.explain-card strong {
  display: block;
  margin-bottom: 4px;
  font-size: 1.15rem;
  line-height: 1.25;
}

.explain-card-wide {
  grid-column: 1 / -1;
}

.explain-label {
  display: block;
  margin-bottom: 6px;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: #627079;
}

.context-grid {
  display: grid;
  gap: 10px;
  margin-top: 10px;
}

.context-card {
  border: 1px solid rgba(124, 145, 159, 0.2);
  border-radius: 8px;
  padding: 10px;
  background: rgba(8, 15, 23, 0.04);
}

.context-card strong {
  display: block;
  margin-bottom: 4px;
  font-size: 1.1rem;
}

.context-card-wide {
  grid-column: 1 / -1;
}

.context-band {
  position: relative;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
  margin: 10px 0 8px;
}

.context-band-segment {
  border: 1px solid rgba(124, 145, 159, 0.2);
  border-radius: 8px;
  background: rgba(8, 15, 23, 0.03);
  padding: 8px 0;
  text-align: center;
  font-size: 0.88rem;
  color: #627079;
}

.context-band-marker {
  position: absolute;
  top: -4px;
  bottom: -4px;
  width: 0;
}

.context-band-marker span {
  display: block;
  width: 2px;
  height: 100%;
  background: #202738;
}

.context-matrix {
  display: grid;
  grid-template-columns: 120px repeat(3, minmax(0, 1fr));
  gap: 6px;
  margin-top: 10px;
}

.context-corner,
.context-header,
.context-cell {
  border: 1px solid rgba(124, 145, 159, 0.2);
  border-radius: 8px;
  padding: 8px;
  background: rgba(8, 15, 23, 0.03);
}

.context-header {
  font-weight: 700;
  font-size: 0.86rem;
  color: #627079;
  text-transform: uppercase;
}

.context-cell strong,
.context-cell span {
  display: block;
}

.context-cell strong {
  margin-bottom: 3px;
  font-size: 0.92rem;
}

.context-cell span {
  color: #627079;
  font-size: 0.85rem;
}

.context-cell-escalates {
  background: rgba(211, 139, 30, 0.08);
}

.context-cell-active {
  border-color: rgba(47, 183, 211, 0.45);
  box-shadow: inset 0 0 0 1px rgba(47, 183, 211, 0.35);
}

.context-guard-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin-top: 10px;
}

@media (max-width: 900px) {
  .explain-grid {
    grid-template-columns: 1fr;
  }

  .explain-card-wide {
    grid-column: auto;
  }

  .context-card-wide {
    grid-column: auto;
  }

  .context-matrix,
  .context-guard-grid {
    grid-template-columns: 1fr;
  }
}
</style>
