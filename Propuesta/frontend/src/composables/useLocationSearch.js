import { computed } from "vue";

export function useLocationSearch({
  locations,
  form,
  result,
  selectedLocationPreset,
  locationSearch,
  loadSensors,
}) {
  const selectedLocationName = computed(() => {
    const byPreset = locations.value.find((item) => String(item.id) === String(form.location_id));
    return byPreset?.name || result.value?.snapshot?.location_name || String(form.location_id || "sin ubicación");
  });

  const filteredLocations = computed(() => {
    const term = locationSearch.value.trim().toLowerCase();
    return locations.value
      .filter((item) => {
        if (!term) {
          return true;
        }
        return [item.name, item.city, item.country, String(item.id)]
          .filter(Boolean)
          .join(" ")
          .toLowerCase()
          .includes(term);
      })
      .slice(0, 6);
  });

  function applySelectedLocation() {
    if (!selectedLocationPreset.value) {
      return;
    }
    form.location_id = selectedLocationPreset.value;
    loadSensors(Number(selectedLocationPreset.value));
  }

  function updateSelectedLocationPreset(value) {
    selectedLocationPreset.value = value;
    applySelectedLocation();
  }

  function selectLocationCard(item) {
    selectedLocationPreset.value = String(item.id);
    form.location_id = String(item.id);
    loadSensors(Number(item.id));
  }

  return {
    applySelectedLocation,
    filteredLocations,
    selectLocationCard,
    selectedLocationName,
    updateSelectedLocationPreset,
  };
}
