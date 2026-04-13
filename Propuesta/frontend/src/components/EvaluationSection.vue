<template>
  <section class="stack">
    <section class="panel">
      <h3>Resultado de evaluación</h3>
      <p class="caption">{{ result.alert.title }}</p>
      <p>{{ result.alert.message }}</p>
      <p v-if="result.alert.caution" class="status-warn">{{ result.alert.caution }}</p>
    </section>

    <section class="panel">
      <h3>Impacto del ajuste contextual</h3>
      <p class="caption">
        Esta lectura compara la salida principal del motor difuso con la salida final después de la
        capa contextual basada en reglas.
      </p>
      <div class="evaluation-metric-grid">
        <div class="evaluation-card">
          <span class="evaluation-label">Salida principal</span>
          <strong>{{ Number(principalTrace.score || 0).toFixed(2) }}</strong>
          <span class="caption">{{ principalTrace.label || "sin etiqueta" }}</span>
        </div>
        <div class="evaluation-card">
          <span class="evaluation-label">Salida final</span>
          <strong>{{ Number(result.fuzzy.score || 0).toFixed(2) }}</strong>
          <span class="caption">{{ result.fuzzy.label }}</span>
        </div>
        <div class="evaluation-card">
          <span class="evaluation-label">Delta contextual</span>
          <strong>{{ contextualDeltaLabel }}</strong>
          <span class="caption">{{ contextualDeltaDescription }}</span>
        </div>
      </div>
    </section>

    <ChartPanel
      title="Ajuste contextual antes y después"
      caption="Compara la salida principal del motor con la salida final tras la capa contextual."
      type="bar"
      :data="contextBeforeAfterChart"
      :options="barOptions"
    />

    <section class="panel">
      <h3>Historial reciente</h3>
      <p class="caption">
        Corridas registradas localmente por el backend. Selecciona una para compararla con la
        corrida actual.
      </p>
      <HistoryFilters
        :filtered-history-count="filteredHistoryItems.length"
        :history-count="historyItems.length"
        :history-date-filter="historyDateFilter"
        :history-filter="historyFilter"
        :history-parameter-filter="historyParameterFilter"
        :history-parameters="historyParameters"
        :history-risk-filter="historyRiskFilter"
        :history-risk-labels="historyRiskLabels"
        @reset="$emit('reset-history-filters')"
        @toggle-parameter="$emit('toggle-history-parameter', $event)"
        @toggle-risk="$emit('toggle-history-risk', $event)"
        @update:history-date-filter="$emit('update:history-date-filter', $event)"
        @update:history-filter="$emit('update:history-filter', $event)"
        @update:history-parameter-filter="$emit('update:history-parameter-filter', $event)"
        @update:history-risk-filter="$emit('update:history-risk-filter', $event)"
      />
      <div class="active-filter-bar">
        <span
          v-for="item in activeHistoryFilters"
          :key="item"
          class="filter-chip active"
        >
          {{ item }}
        </span>
        <span v-if="activeHistoryFilters.length === 0" class="filter-chip">Sin filtros activos</span>
      </div>

      <div class="history-layout">
        <ul class="history-list history-list-dense">
          <li v-if="filteredHistoryItems.length === 0" class="history-empty">
            Sin corridas registradas.
          </li>
          <li v-for="item in filteredHistoryItems" :key="item.recorded_at">
            <button
              class="history-button history-card"
              :class="{ active: selectedHistoryItem?.recorded_at === item.recorded_at }"
              type="button"
              @click="$emit('select-history-item', item)"
            >
              <div class="history-card-head">
                <strong>{{ item.summary.location_name || "sin ubicación" }}</strong>
                <span class="history-time">{{ formatRecordedAt(item.recorded_at) }}</span>
              </div>
              <div class="history-card-meta">
                <span class="filter-chip">AQI {{ item.summary.aqi_global ?? "NR" }}</span>
                <span class="filter-chip">{{ humanizeLabel(item.summary.fuzzy_label) }}</span>
                <span class="filter-chip">{{ item.summary.dominant_parameter || "sin dominante" }}</span>
                <span class="filter-chip">{{ item.summary.source || "sin fuente" }}</span>
              </div>
              <span class="history-card-note">
                Cobertura {{ formatPercent(item.summary.coverage_global) }} ·
                {{ item.summary.context_adjustments?.length || 0 }} ajuste(s) contextuales ·
                {{ item.summary.triggered_rules?.length || 0 }} regla(s) activadas
              </span>
            </button>
          </li>
        </ul>

        <article v-if="selectedHistoryItem" class="history-focus-card">
          <span class="eyebrow">Corrida histórica seleccionada</span>
          <h4>{{ selectedHistoryItem.summary.location_name || "sin ubicación" }}</h4>
          <p class="caption">
            {{ formatRecordedAt(selectedHistoryItem.recorded_at) }} ·
            {{ selectedHistoryItem.summary.source || "sin fuente" }}
          </p>
          <div class="evaluation-metric-grid history-detail-grid">
            <div class="evaluation-card">
              <span class="evaluation-label">AQI histórico</span>
              <strong>{{ selectedHistoryItem.summary.aqi_global ?? "NR" }}</strong>
              <span class="caption">
                Dominante {{ selectedHistoryItem.summary.dominant_parameter || "sin dominante" }}
              </span>
            </div>
            <div class="evaluation-card">
              <span class="evaluation-label">Salida histórica</span>
              <strong>{{ Number(selectedHistoryItem.summary.fuzzy_score ?? 0).toFixed(2) }}</strong>
              <span class="caption">{{ humanizeLabel(selectedHistoryItem.summary.fuzzy_label) }}</span>
            </div>
            <div class="evaluation-card">
              <span class="evaluation-label">Cobertura histórica</span>
              <strong>{{ formatPercent(selectedHistoryItem.summary.coverage_global) }}</strong>
              <span class="caption">
                {{ selectedHistoryItem.summary.context_adjustments?.length || 0 }} ajuste(s) contextuales
              </span>
            </div>
          </div>
          <div class="history-detail-tags">
            <span
              v-for="item in selectedHistoryItem.summary.context_adjustments || []"
              :key="item"
              class="filter-chip active"
            >
              {{ item }}
            </span>
            <span
              v-if="!(selectedHistoryItem.summary.context_adjustments || []).length"
              class="filter-chip"
            >
              Sin ajuste contextual
            </span>
          </div>
        </article>
      </div>
    </section>

    <ChartPanel
      v-if="selectedHistoryItem"
      title="Comparación histórica de riesgo"
      caption="Contrasta la corrida actual con la corrida histórica seleccionada en escalas equivalentes de AQI base y salida final."
      type="bar"
      :data="historyRiskComparisonChart"
      :options="barOptions"
    />

    <ChartPanel
      v-if="selectedHistoryItem"
      title="Comparación histórica de cobertura"
      caption="Compara solo la completitud de datos de ambas corridas, fuera de la malla difusa."
      type="bar"
      :data="historyCoverageChart"
      :options="barOptions"
    />
  </section>
</template>

<script setup>
import { computed } from "vue";
import ChartPanel from "./ChartPanel.vue";
import HistoryFilters from "./HistoryFilters.vue";

const props = defineProps({
  activeHistoryFilters: { type: Array, required: true },
  barOptions: { type: Object, required: true },
  contextTrace: { type: Object, required: true },
  contextBeforeAfterChart: { type: Object, required: true },
  filteredHistoryItems: { type: Array, required: true },
  historyCoverageChart: { type: Object, required: true },
  historyDateFilter: { type: String, default: "" },
  historyFilter: { type: String, default: "" },
  historyItems: { type: Array, required: true },
  historyParameterFilter: { type: String, default: "" },
  historyParameters: { type: Array, required: true },
  historyRiskFilter: { type: String, default: "" },
  historyRiskLabels: { type: Array, required: true },
  historyRiskComparisonChart: { type: Object, required: true },
  principalTrace: { type: Object, required: true },
  result: { type: Object, required: true },
  selectedHistoryItem: { type: Object, default: null },
});

defineEmits([
  "reset-history-filters",
  "select-history-item",
  "toggle-history-parameter",
  "toggle-history-risk",
  "update:history-date-filter",
  "update:history-filter",
  "update:history-parameter-filter",
  "update:history-risk-filter",
]);

const contextualDelta = computed(() => Number(props.result.fuzzy?.score || 0) - Number(props.principalTrace?.score || 0));
const contextualDeltaLabel = computed(() => `${contextualDelta.value >= 0 ? "+" : ""}${contextualDelta.value.toFixed(2)}`);
const contextualDeltaDescription = computed(() => {
  if (props.contextTrace?.applied) {
    return `La capa contextual aplicó ${props.contextTrace.escalation || 0} nivel(es) mediante ${props.contextTrace.rule}.`;
  }
  if (props.contextTrace?.rule) {
    return `La regla ${props.contextTrace.rule} fue evaluada, pero no modificó la salida principal.`;
  }
  return "No hubo variables contextuales válidas para evaluar la capa contextual.";
});

function formatRecordedAt(value) {
  if (!value) {
    return "sin fecha";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return new Intl.DateTimeFormat("es-EC", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function formatPercent(value) {
  if (value == null || value === "") {
    return "NR";
  }
  return `${Number(value).toFixed(1)}%`;
}

function humanizeLabel(value) {
  return String(value || "sin etiqueta").replaceAll("_", " ");
}
</script>

<style scoped>
.evaluation-metric-grid {
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  margin-top: 10px;
}

.evaluation-card {
  border: 1px solid rgba(124, 145, 159, 0.2);
  border-radius: 8px;
  padding: 10px;
  background: rgba(8, 15, 23, 0.04);
}

.evaluation-card strong {
  display: block;
  margin-bottom: 4px;
  font-size: 1.15rem;
}

.evaluation-label {
  display: block;
  margin-bottom: 6px;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: #627079;
}

.history-layout {
  display: grid;
  gap: 12px;
  grid-template-columns: minmax(320px, 0.9fr) minmax(0, 1.1fr);
}

.history-list-dense {
  max-height: 420px;
  overflow: auto;
  padding-right: 4px;
}

.history-empty {
  color: #627079;
}

.history-card {
  display: grid;
  gap: 8px;
  text-align: left;
}

.history-card-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 8px;
}

.history-time {
  color: #627079;
  font-size: 0.86rem;
}

.history-card-meta,
.history-detail-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.history-card-note {
  color: #627079;
  font-size: 0.9rem;
  line-height: 1.4;
}

.history-detail-grid {
  margin: 10px 0;
}

@media (max-width: 900px) {
  .evaluation-metric-grid {
    grid-template-columns: 1fr;
  }

  .history-layout {
    grid-template-columns: 1fr;
  }

  .history-list-dense {
    max-height: none;
  }
}
</style>
