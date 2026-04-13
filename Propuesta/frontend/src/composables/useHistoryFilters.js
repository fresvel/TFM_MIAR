import { computed, watch } from "vue";

export function useHistoryFilters({
  historyItems,
  historyFilter,
  historyDateFilter,
  historyParameterFilter,
  historyRiskFilter,
  selectedHistoryItem,
}) {
  const filteredHistoryItems = computed(() => {
    const term = historyFilter.value.trim().toLowerCase();
    return historyItems.value.filter((item) => {
      const haystack = [
        item.recorded_at,
        item.summary.location_name,
        item.summary.fuzzy_label,
        item.summary.dominant_parameter,
        String(item.summary.aqi_global ?? ""),
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
      const matchesText = !term || haystack.includes(term);
      const matchesDate =
        !historyDateFilter.value || String(item.recorded_at || "").startsWith(historyDateFilter.value);
      const matchesParameter =
        !historyParameterFilter.value ||
        String(item.summary.dominant_parameter || "") === historyParameterFilter.value;
      const matchesRisk =
        !historyRiskFilter.value || String(item.summary.fuzzy_label || "") === historyRiskFilter.value;
      return matchesText && matchesDate && matchesParameter && matchesRisk;
    });
  });

  const historyParameters = computed(() => {
    return [...new Set(historyItems.value.map((item) => item.summary.dominant_parameter).filter(Boolean))];
  });

  const historyRiskLabels = computed(() => {
    return [...new Set(historyItems.value.map((item) => item.summary.fuzzy_label).filter(Boolean))];
  });

  const activeHistoryFilters = computed(() => {
    return [
      historyFilter.value ? `Texto: ${historyFilter.value}` : "",
      historyDateFilter.value ? `Fecha: ${historyDateFilter.value}` : "",
      historyParameterFilter.value ? `Parámetro: ${historyParameterFilter.value}` : "",
      historyRiskFilter.value ? `Riesgo: ${historyRiskFilter.value}` : "",
    ].filter(Boolean);
  });

  function resetHistoryFilters() {
    historyFilter.value = "";
    historyDateFilter.value = "";
    historyParameterFilter.value = "";
    historyRiskFilter.value = "";
  }

  function toggleHistoryParameter(parameter) {
    historyParameterFilter.value = historyParameterFilter.value === parameter ? "" : parameter;
  }

  function toggleHistoryRisk(riskLabel) {
    historyRiskFilter.value = historyRiskFilter.value === riskLabel ? "" : riskLabel;
  }

  watch(
    filteredHistoryItems,
    (items) => {
      if (!items.length) {
        selectedHistoryItem.value = null;
        return;
      }
      const currentId = selectedHistoryItem.value?.recorded_at;
      if (!currentId || !items.some((item) => item.recorded_at === currentId)) {
        selectedHistoryItem.value = items[0];
      }
    },
    { immediate: true },
  );

  return {
    activeHistoryFilters,
    filteredHistoryItems,
    historyParameters,
    historyRiskLabels,
    resetHistoryFilters,
    toggleHistoryParameter,
    toggleHistoryRisk,
  };
}
