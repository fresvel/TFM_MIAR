<template>
  <section class="stack">
    <section class="panel">
      <h3>Resultado de evaluación</h3>
      <p class="caption">{{ result.alert.title }}</p>
      <p>{{ result.alert.message }}</p>
      <p v-if="result.alert.caution" class="status-warn">{{ result.alert.caution }}</p>
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
      <ul class="history-list">
        <li v-if="filteredHistoryItems.length === 0">Sin corridas registradas.</li>
        <li v-for="item in filteredHistoryItems" :key="item.recorded_at">
          <button
            class="history-button"
            :class="{ active: selectedHistoryItem?.recorded_at === item.recorded_at }"
            type="button"
            @click="$emit('select-history-item', item)"
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
      <article v-if="selectedHistoryItem" class="history-focus-card">
        <span class="eyebrow">Corrida histórica seleccionada</span>
        <h4>{{ selectedHistoryItem.summary.location_name || "sin ubicación" }}</h4>
        <p class="caption">
          {{ selectedHistoryItem.recorded_at }} · AQI {{ selectedHistoryItem.summary.aqi_global ?? "NR" }} ·
          {{ selectedHistoryItem.summary.fuzzy_label }}.
        </p>
        <p>
          Dominante {{ selectedHistoryItem.summary.dominant_parameter || "sin dominante" }} con cobertura
          {{ selectedHistoryItem.summary.coverage_global ?? "NR" }}.
        </p>
      </article>
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
</template>

<script setup>
import ChartPanel from "./ChartPanel.vue";
import HistoryFilters from "./HistoryFilters.vue";

defineProps({
  activeHistoryFilters: { type: Array, required: true },
  barOptions: { type: Object, required: true },
  contextBeforeAfterChart: { type: Object, required: true },
  filteredHistoryItems: { type: Array, required: true },
  historyComparisonChart: { type: Object, required: true },
  historyDateFilter: { type: String, default: "" },
  historyFilter: { type: String, default: "" },
  historyItems: { type: Array, required: true },
  historyParameterFilter: { type: String, default: "" },
  historyParameters: { type: Array, required: true },
  historyRiskFilter: { type: String, default: "" },
  historyRiskLabels: { type: Array, required: true },
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
</script>
