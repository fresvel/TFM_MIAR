<template>
  <section class="stack">
    <section class="panel">
      <h3>Series temporales por contaminante</h3>
      <p class="caption">
        La visualización permite inspeccionar el recorrido reciente de cada parámetro recuperado.
      </p>
      <div class="inline-field">
        <label for="seriesParameter">Parámetro</label>
        <select
          id="seriesParameter"
          :value="selectedSeriesParameter"
          @change="$emit('update:selected-series-parameter', $event.target.value)"
        >
          <option v-for="item in availableSeriesParameters" :key="item" :value="item">
            {{ item }}
          </option>
        </select>
      </div>
    </section>

    <ChartPanel
      title="Serie temporal filtrada"
      caption="Observaciones recientes del parámetro seleccionado."
      type="line"
      :data="timeSeriesChart"
      :options="seriesLineOptions"
    />

    <ChartPanel
      title="Subíndices AQI y umbrales normativos"
      caption="Las barras muestran el subíndice AQI por contaminante; las líneas punteadas marcan umbrales EPA y la barra dominante queda resaltada."
      type="bar"
      :data="subindicesChart"
      :options="subindicesChartOptions"
    />

    <section class="panel">
      <h3>Lectura de síntesis</h3>
      <p class="caption">
        La lectura final se separa en dos capas: comparación normativa-difusa por un lado y
        variables auxiliares del motor por otro.
      </p>
    </section>

    <div class="dashboard-synthesis-grid">
      <ChartPanel
        title="Escala AQI: base frente a salida difusa"
        caption="Compara la salida normativa inicial con la puntuación final del motor en la misma escala AQI."
        type="bar"
        :data="baseVsFinalChart"
        :options="barOptions"
      />

      <ChartPanel
        title="Entradas auxiliares del motor difuso"
        caption="Persistencia y concurrencia son puntajes auxiliares; cobertura se añade como indicador de calidad de datos."
        type="bar"
        :data="auxiliaryChart"
        :options="barOptions"
      />
    </div>
  </section>
</template>

<script setup>
import ChartPanel from "./ChartPanel.vue";

defineProps({
  auxiliaryChart: { type: Object, required: true },
  availableSeriesParameters: { type: Array, required: true },
  barOptions: { type: Object, required: true },
  baseVsFinalChart: { type: Object, required: true },
  selectedSeriesParameter: { type: String, required: true },
  seriesLineOptions: { type: Object, required: true },
  subindicesChart: { type: Object, required: true },
  subindicesChartOptions: { type: Object, required: true },
  timeSeriesChart: { type: Object, required: true },
});

defineEmits(["update:selected-series-parameter"]);
</script>

<style scoped>
.dashboard-synthesis-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

@media (max-width: 980px) {
  .dashboard-synthesis-grid {
    grid-template-columns: 1fr;
  }
}
</style>
