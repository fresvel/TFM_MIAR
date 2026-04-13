<template>
  <div>
    <div class="filter-grid">
      <div class="field">
        <label for="historyFilter">Texto</label>
        <input
          id="historyFilter"
          :value="historyFilter"
          type="text"
          placeholder="Ubicación, etiqueta o AQI"
          @input="$emit('update:history-filter', $event.target.value)"
        />
      </div>
      <div class="field">
        <label for="historyDate">Fecha</label>
        <input
          id="historyDate"
          :value="historyDateFilter"
          type="date"
          @input="$emit('update:history-date-filter', $event.target.value)"
        />
      </div>
      <div class="field">
        <label for="historyParameter">Parámetro dominante</label>
        <select
          id="historyParameter"
          :value="historyParameterFilter"
          @change="$emit('update:history-parameter-filter', $event.target.value)"
        >
          <option value="">Todos</option>
          <option v-for="item in historyParameters" :key="item" :value="item">
            {{ item }}
          </option>
        </select>
      </div>
      <div class="field">
        <label for="historyRisk">Riesgo</label>
        <select
          id="historyRisk"
          :value="historyRiskFilter"
          @change="$emit('update:history-risk-filter', $event.target.value)"
        >
          <option value="">Todos</option>
          <option v-for="item in historyRiskLabels" :key="item" :value="item">
            {{ item }}
          </option>
        </select>
      </div>
    </div>

    <div class="history-toolbar">
      <span class="caption">
        {{ filteredHistoryCount }} coincidencia(s) sobre {{ historyCount }} registro(s).
      </span>
      <button class="secondary" type="button" @click="$emit('reset')">Limpiar filtros</button>
    </div>

    <div class="chip-row">
      <button
        v-for="item in historyParameters"
        :key="`param-${item}`"
        class="filter-chip"
        :class="{ active: historyParameterFilter === item }"
        type="button"
        @click="$emit('toggle-parameter', item)"
      >
        {{ item }}
      </button>
    </div>

    <div class="chip-row">
      <button
        v-for="item in historyRiskLabels"
        :key="`risk-${item}`"
        class="filter-chip"
        :class="{ active: historyRiskFilter === item }"
        type="button"
        @click="$emit('toggle-risk', item)"
      >
        {{ item }}
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  filteredHistoryCount: { type: Number, required: true },
  historyCount: { type: Number, required: true },
  historyDateFilter: { type: String, default: "" },
  historyFilter: { type: String, default: "" },
  historyParameterFilter: { type: String, default: "" },
  historyParameters: { type: Array, required: true },
  historyRiskFilter: { type: String, default: "" },
  historyRiskLabels: { type: Array, required: true },
});

defineEmits([
  "reset",
  "toggle-parameter",
  "toggle-risk",
  "update:history-date-filter",
  "update:history-filter",
  "update:history-parameter-filter",
  "update:history-risk-filter",
]);
</script>
