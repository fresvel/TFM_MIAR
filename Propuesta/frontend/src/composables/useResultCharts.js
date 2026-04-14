import { computed } from "vue";

import { AQI_THRESHOLDS, CHART_PALETTE } from "../config/chartOptions";
import { aqiBandColor } from "../utils/aqi";

function buildMembershipChart(curves, inputValue) {
  const entries = Object.entries(curves || {});
  return {
    datasets: [
      ...entries.map(([term, points], index) => ({
        label: term,
        data: points.map((item) => ({ x: item.x, y: item.membership })),
        borderColor: CHART_PALETTE[index % CHART_PALETTE.length],
        backgroundColor: "transparent",
        tension: 0.22,
      })),
      ...(typeof inputValue === "number" && Number.isFinite(inputValue)
        ? [
            {
              label: "entrada actual",
              data: [
                { x: inputValue, y: 0 },
                { x: inputValue, y: 1 },
              ],
              borderColor: "#202738",
              borderDash: [6, 4],
              pointRadius: 0,
              fill: false,
              tension: 0,
            },
          ]
        : []),
    ],
  };
}

export function useResultCharts({
  metadata,
  principalTrace,
  result,
  selectedHistoryItem,
  selectedSeriesParameter,
}) {
  const availableSeriesParameters = computed(() => Object.keys(result.value?.snapshot?.series || {}));

  const subindicesChart = computed(() => {
    const labels = Object.keys(result.value?.aqi?.subindices || {});
    const dominant = result.value?.aqi?.dominant_parameter;
    const values = labels.map((label) => result.value.aqi.subindices[label]);
    return {
      labels,
      datasets: [
        {
          label: "Subíndice AQI",
          data: values,
          backgroundColor: labels.map((label, index) => aqiBandColor(values[index], label === dominant)),
          borderColor: labels.map((label, index) =>
            label === dominant ? "#202738" : aqiBandColor(values[index], true),
          ),
          borderWidth: labels.map((label) => (label === dominant ? 2 : 1)),
          borderRadius: 6,
        },
        ...AQI_THRESHOLDS
          .filter((item) => !values.length || Math.max(...values, 0) >= item.value - 20)
          .map((item) => ({
            type: "line",
            label: `Umbral ${item.label} (${item.value})`,
            data: labels.map(() => item.value),
            borderColor: item.color,
            borderDash: [6, 6],
            borderWidth: 1.5,
            pointRadius: 0,
            pointHoverRadius: 0,
            fill: false,
          })),
      ],
    };
  });

  const subindicesChartOptions = computed(() => ({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: "bottom",
        labels: {
          color: "#627079",
          boxWidth: 18,
        },
      },
    },
    scales: {
      x: { grid: { display: false }, ticks: { color: "#627079" } },
      y: {
        beginAtZero: true,
        suggestedMax: Math.max(result.value?.aqi?.global_aqi || 0, 160),
        grid: { color: "rgba(23, 33, 39, 0.08)" },
        ticks: { color: "#627079" },
        title: {
          display: true,
          text: "Subíndice AQI",
          color: "#627079",
        },
      },
    },
  }));

  const baseVsFinalChart = computed(() => ({
    labels: ["AQI base", "Puntuación difusa"],
    datasets: [
      {
        data: [result.value?.aqi?.global_aqi || 0, result.value?.fuzzy?.score || 0],
        backgroundColor: ["#2fb7d3", "#46b34d"],
        borderRadius: 6,
      },
    ],
  }));

  const auxiliaryChart = computed(() => ({
    labels: ["Concurrencia", "Persistencia", "Cobertura"],
    datasets: [
      {
        data: [
          result.value?.concurrence_score || 0,
          result.value?.persistence_score || 0,
          result.value?.snapshot?.coverage_global || 0,
        ],
        backgroundColor: ["#d38b1e", "#d15e43", "#46b34d"],
        borderRadius: 6,
      },
    ],
  }));

  const triggeredRulesChart = computed(() => {
    const rules = result.value?.explainability?.layer_outputs?.inferencia_difusa_principal?.rules || [];
    const orderedRules = [...rules].sort((left, right) => right.strength - left.strength);
    return {
      labels: orderedRules.length ? orderedRules.map((rule) => rule.name) : ["sin reglas"],
      datasets: [
        {
          data: orderedRules.length ? orderedRules.map((rule) => rule.strength) : [0],
          backgroundColor: "#2fb7d3",
          borderRadius: 6,
        },
      ],
    };
  });

  const timeSeriesChart = computed(() => {
    const observations = result.value?.snapshot?.series?.[selectedSeriesParameter.value]?.observations || [];
    return {
      labels: observations.map((item) => item.datetime_to),
      datasets: [
        {
          label: selectedSeriesParameter.value,
          data: observations.map((item) => item.value),
          borderColor: "#0f8f8a",
          backgroundColor: "rgba(15, 143, 138, 0.14)",
          fill: true,
          tension: 0.22,
        },
      ],
    };
  });

  const aggregationChart = computed(() => {
    const points = principalTrace.value?.aggregation_samples || [];
    const principalScoreValue = principalTrace.value?.score || 0;
    const nearestSample =
      points.reduce(
        (best, item) =>
          Math.abs(item.x - principalScoreValue) < Math.abs(best.x - principalScoreValue) ? item : best,
        { x: 0, membership: 0 },
      ) || { x: principalScoreValue, membership: 0 };
    return {
      datasets: [
        {
          label: "Agregación difusa",
          data: points.map((item) => ({ x: item.x, y: item.membership })),
          borderColor: "#202738",
          backgroundColor: "rgba(32, 39, 56, 0.14)",
          fill: true,
          tension: 0.25,
        },
        {
          label: "Score principal",
          data: [{ x: principalScoreValue, y: nearestSample.membership || 0 }],
          borderColor: "#d15e43",
          backgroundColor: "#d15e43",
          pointRadius: 5,
          pointHoverRadius: 6,
          showLine: false,
        },
      ],
    };
  });

  const contextBeforeAfterChart = computed(() => {
    const before = result.value?.explainability?.layer_outputs?.inferencia_difusa_principal?.score || 0;
    const after = result.value?.fuzzy?.score || 0;
    return {
      labels: ["Salida principal", "Salida final"],
      datasets: [
        {
          data: [before, after],
          backgroundColor: ["#d38b1e", "#46b34d"],
          borderRadius: 6,
        },
      ],
    };
  });

  const historyRiskComparisonChart = computed(() => {
    const current = result.value;
    const previous = selectedHistoryItem.value;
    return {
      labels: ["AQI base", "Puntuación final"],
      datasets: [
        {
          label: "Actual",
          data: [current?.aqi?.global_aqi || 0, current?.fuzzy?.score || 0],
          backgroundColor: "#2fb7d3",
          borderRadius: 6,
        },
        {
          label: "Histórica",
          data: [previous?.summary?.aqi_global || 0, previous?.summary?.fuzzy_score || 0],
          backgroundColor: "#0f8f8a",
          borderRadius: 6,
        },
      ],
    };
  });

  const historyCoverageChart = computed(() => {
    const current = result.value;
    const previous = selectedHistoryItem.value;
    return {
      labels: ["Cobertura"],
      datasets: [
        {
          label: "Actual",
          data: [current?.snapshot?.coverage_global || 0],
          backgroundColor: "#46b34d",
          borderRadius: 6,
        },
        {
          label: "Histórica",
          data: [previous?.summary?.coverage_global || 0],
          backgroundColor: "#d38b1e",
          borderRadius: 6,
        },
      ],
    };
  });

  const aqiMembershipChart = computed(() =>
    buildMembershipChart(metadata.model.membership_curves?.aqi, principalTrace.value?.inputs?.aqi),
  );
  const concurrenceMembershipChart = computed(() =>
    buildMembershipChart(
      metadata.model.membership_curves?.concurrence,
      principalTrace.value?.inputs?.concurrence,
    ),
  );
  const persistenceMembershipChart = computed(() =>
    buildMembershipChart(
      metadata.model.membership_curves?.persistence,
      principalTrace.value?.inputs?.persistence,
    ),
  );

  return {
    aggregationChart,
    aqiMembershipChart,
    auxiliaryChart,
    availableSeriesParameters,
    baseVsFinalChart,
    concurrenceMembershipChart,
    contextBeforeAfterChart,
    historyCoverageChart,
    historyRiskComparisonChart,
    persistenceMembershipChart,
    subindicesChart,
    subindicesChartOptions,
    timeSeriesChart,
    triggeredRulesChart,
  };
}
