export const BAR_OPTIONS = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
  },
  scales: {
    x: { grid: { display: false }, ticks: { color: "#627079" } },
    y: {
      beginAtZero: true,
      grid: { color: "rgba(23, 33, 39, 0.08)" },
      ticks: { color: "#627079" },
    },
  },
};

export const LINE_OPTIONS = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
  },
  scales: {
    x: { type: "linear", grid: { color: "rgba(23, 33, 39, 0.08)" }, ticks: { color: "#627079" } },
    y: { beginAtZero: true, max: 1.05, grid: { color: "rgba(23, 33, 39, 0.08)" }, ticks: { color: "#627079" } },
  },
};

export const LINE_OPTIONS_WITH_LEGEND = {
  ...LINE_OPTIONS,
  plugins: {
    legend: { display: true, position: "bottom" },
  },
};

export const SERIES_LINE_OPTIONS = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
  },
  scales: {
    x: { grid: { color: "rgba(23, 33, 39, 0.06)" } },
    y: { beginAtZero: true, grid: { color: "rgba(23, 33, 39, 0.06)" } },
  },
};

export const CHART_PALETTE = ["#2fb7d3", "#0f8f8a", "#46b34d", "#d38b1e", "#d15e43", "#202738"];

export const AQI_THRESHOLDS = [
  { label: "Bueno", value: 50, color: "#46b34d" },
  { label: "Moderado", value: 100, color: "#d38b1e" },
  { label: "Sensibles", value: 150, color: "#d15e43" },
  { label: "Dañino", value: 200, color: "#9a3412" },
];
