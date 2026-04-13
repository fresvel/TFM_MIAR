<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <div class="sidebar-header-row">
        <span class="eyebrow">Vistas</span>
        <div class="hover-help">
          <button class="help-trigger" type="button" aria-label="Ayuda sobre navegación">i</button>
          <span class="help-bubble">Navega por bloques de análisis, trazabilidad y evaluación del artefacto.</span>
        </div>
      </div>
    </div>

    <div class="nav-group">
      <button
        v-for="item in sections"
        :key="item.id"
        class="nav-button"
        :class="{ active: currentSection === item.id, disabled: !hasResult }"
        :disabled="!hasResult"
        @click="$emit('open-viewer', item.id)"
      >
        {{ item.label }}
      </button>
    </div>

    <section v-if="hasResult" class="sidebar-panel sidebar-panel-strong">
      <span class="eyebrow">Corrida actual</span>
      <h3>{{ result.fuzzy?.label || "Sin resultado" }}</h3>
      <p class="sidebar-note">
        AQI {{ result.aqi?.global_aqi ?? "NR" }} · {{ result.aqi?.dominant_parameter || "sin dominante" }}
      </p>
      <div class="sidebar-pill-row">
        <span class="status-pill" :class="riskTone">Riesgo</span>
        <span class="status-pill" :class="coverageTone">{{ result.snapshot?.coverage_global ?? "NR" }}%</span>
      </div>
    </section>
  </aside>
</template>

<script setup>
defineProps({
  coverageTone: { type: String, default: "" },
  currentSection: { type: String, required: true },
  hasResult: { type: Boolean, required: true },
  result: { type: Object, default: null },
  riskTone: { type: String, default: "" },
  sections: { type: Array, required: true },
});

defineEmits(["open-viewer"]);
</script>
