<template>
  <section class="panel">
    <div class="chart-panel-head">
      <h3>{{ title }}</h3>
      <button class="secondary chart-download" type="button" @click="downloadChart">
        Descargar PNG
      </button>
    </div>
    <p v-if="caption" class="caption">{{ caption }}</p>
    <div class="chart-wrap">
      <canvas ref="canvasRef"></canvas>
    </div>
  </section>
</template>

<script setup>
import { Chart, BarController, BarElement, CategoryScale, LinearScale, LineController, LineElement, PointElement, Tooltip, Legend, Filler } from "chart.js";
import { onBeforeUnmount, onMounted, ref, watch } from "vue";

Chart.register(
  BarController,
  BarElement,
  CategoryScale,
  LinearScale,
  LineController,
  LineElement,
  PointElement,
  Tooltip,
  Legend,
  Filler,
);

const props = defineProps({
  title: { type: String, required: true },
  caption: { type: String, default: "" },
  type: { type: String, default: "bar" },
  data: { type: Object, required: true },
  options: { type: Object, default: () => ({ responsive: true, maintainAspectRatio: false }) },
});

const canvasRef = ref(null);
let chartInstance = null;

function buildFilename() {
  return `${props.title
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "") || "chart"}.png`;
}

function downloadChart() {
  if (!chartInstance) {
    return;
  }
  const url = chartInstance.toBase64Image("image/png", 1);
  const link = document.createElement("a");
  link.href = url;
  link.download = buildFilename();
  link.click();
}

function renderChart() {
  if (!canvasRef.value) {
    return;
  }
  if (chartInstance) {
    chartInstance.destroy();
  }
  chartInstance = new Chart(canvasRef.value, {
    type: props.type,
    data: props.data,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      ...props.options,
    },
  });
}

onMounted(renderChart);
watch(() => props.data, renderChart, { deep: true });
watch(() => props.type, renderChart);
watch(() => props.options, renderChart, { deep: true });

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.destroy();
  }
});
</script>

<style scoped>
.chart-panel-head {
  align-items: center;
  display: flex;
  gap: 12px;
  justify-content: space-between;
}

.chart-download {
  flex-shrink: 0;
}
</style>
