<template>
  <section class="stack">
    <ChartPanel
      title="Distribución de reglas activadas"
      caption="La gráfica refleja cuántas reglas se activaron en esta corrida."
      type="bar"
      :data="triggeredRulesChart"
      :options="barOptions"
    />

    <ChartPanel
      title="Agregación y defuzzificación"
      caption="Curva agregada del sistema difuso para la corrida actual."
      type="line"
      :data="aggregationChart"
      :options="lineOptions"
    />

    <ChartPanel
      title="Funciones de pertenencia del AQI"
      caption="Curvas base utilizadas por el motor para la variable AQI."
      type="line"
      :data="aqiMembershipChart"
      :options="lineOptionsWithLegend"
    />

    <ChartPanel
      title="Funciones de pertenencia de concurrencia"
      caption="Curvas base utilizadas para la variable de concurrencia."
      type="line"
      :data="concurrenceMembershipChart"
      :options="lineOptionsWithLegend"
    />

    <ChartPanel
      title="Funciones de pertenencia de persistencia"
      caption="Curvas base utilizadas para la variable de persistencia."
      type="line"
      :data="persistenceMembershipChart"
      :options="lineOptionsWithLegend"
    />

    <section class="panel">
      <h3>Lectura explicable del episodio</h3>
      <p class="caption">
        Dominante: <strong>{{ result.aqi.dominant_parameter || "sin dominante" }}</strong>.
        Concurrencia: <strong>{{ result.concurrence_score }}</strong>.
        Persistencia: <strong>{{ result.persistence_score }}</strong>.
        Salida final: <strong>{{ result.fuzzy.label }}</strong>.
      </p>
      <p class="caption">
        La salida principal del motor puede compararse con la salida final en la vista de evaluación
        cuando existe ajuste contextual.
      </p>
    </section>
  </section>
</template>

<script setup>
import ChartPanel from "./ChartPanel.vue";

defineProps({
  aggregationChart: { type: Object, required: true },
  aqiMembershipChart: { type: Object, required: true },
  barOptions: { type: Object, required: true },
  concurrenceMembershipChart: { type: Object, required: true },
  lineOptions: { type: Object, required: true },
  lineOptionsWithLegend: { type: Object, required: true },
  persistenceMembershipChart: { type: Object, required: true },
  result: { type: Object, required: true },
  triggeredRulesChart: { type: Object, required: true },
});
</script>
