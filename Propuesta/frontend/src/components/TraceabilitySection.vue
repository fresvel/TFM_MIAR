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
    <article class="trace-box">
      <h4>Parámetros soportados</h4>
      <div class="tag-list">
        <span v-for="item in result.aqi.supported_parameters" :key="item" class="tag">{{ item }}</span>
      </div>
    </article>
    <article class="trace-box">
      <h4>Parámetros no soportados</h4>
      <div class="tag-list">
        <span v-for="item in result.aqi.unsupported_parameters" :key="item" class="tag">{{ item }}</span>
      </div>
    </article>
    <article class="trace-box">
      <h4>Reglas activadas</h4>
      <ul>
        <li v-if="activatedRuleDetails.length === 0">Sin reglas activadas.</li>
        <li v-for="rule in activatedRuleDetails" :key="rule.name">
          <strong>{{ rule.name }}</strong>
          · fuerza {{ rule.strengthLabel }}
          · salida {{ rule.outputLabel }}
        </li>
      </ul>
    </article>
    <article class="trace-box">
      <h4>Ajustes contextuales</h4>
      <ul>
        <li v-if="result.context_adjustments.length === 0">Sin ajuste contextual.</li>
        <li v-for="item in result.context_adjustments" :key="item">{{ item }}</li>
      </ul>
    </article>
    <article class="trace-box">
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
defineProps({
  activatedRuleDetails: { type: Array, required: true },
  result: { type: Object, required: true },
  sensors: { type: Array, required: true },
});
</script>
