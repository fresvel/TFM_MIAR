<template>
  <section class="executive-panel">
    <div class="executive-copy">
      <span class="eyebrow">Lectura ejecutiva</span>
      <h3>{{ narrative.title }}</h3>
      <p>{{ narrative.body }}</p>
    </div>
    <div class="executive-metrics">
      <article
        v-for="metric in metrics"
        :key="metric.label"
        class="executive-metric"
        :class="metric.tone"
      >
        <span>{{ metric.label }}</span>
        <strong>{{ metric.value }}</strong>
        <small>{{ metric.helper }}</small>
      </article>
    </div>
    <div class="executive-actions">
      <button class="primary" type="button" @click="$emit('open-section', 'evaluation')">
        Abrir evaluación
      </button>
      <button class="secondary" type="button" @click="$emit('open-section', 'explainability')">
        Revisar explicabilidad
      </button>
    </div>
  </section>
</template>

<script setup>
defineProps({
  narrative: {
    type: Object,
    required: true,
  },
  metrics: {
    type: Array,
    required: true,
  },
});

defineEmits(["open-section"]);
</script>
