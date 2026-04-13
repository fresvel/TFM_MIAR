<template>
  <div>
    <div class="form-grid">
      <div class="field">
        <label for="locationPreset">Ubicación sugerida</label>
        <select
          id="locationPreset"
          :value="selectedLocationPreset"
          @change="$emit('update:selected-location-preset', $event.target.value)"
        >
          <option value="">Seleccionar ubicación</option>
          <option v-for="item in locations" :key="item.id" :value="String(item.id)">
            {{ item.name }}{{ item.city ? ` · ${item.city}` : "" }}
          </option>
        </select>
      </div>

      <div class="field">
        <label for="locationSearch">Filtro de ubicaciones</label>
        <input
          id="locationSearch"
          :value="locationSearch"
          type="text"
          placeholder="Buscar por nombre, ciudad o país"
          @input="$emit('update:location-search', $event.target.value)"
        />
      </div>

      <button class="nav-button" type="button" @click="$emit('refresh-locations')">
        Actualizar ubicaciones
      </button>
    </div>

    <div v-if="filteredLocations.length" class="location-suggestion-grid">
      <button
        v-for="item in filteredLocations"
        :key="item.id"
        class="location-card"
        :class="{ active: String(item.id) === String(locationId) }"
        type="button"
        @click="$emit('select-location-card', item)"
      >
        <strong>{{ item.name }}</strong>
        <span>{{ item.city || "Sin ciudad" }} · {{ item.country || "—" }}</span>
        <small>ID {{ item.id }}</small>
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  filteredLocations: { type: Array, required: true },
  locationId: { type: [String, Number], default: "" },
  locationSearch: { type: String, default: "" },
  locations: { type: Array, required: true },
  selectedLocationPreset: { type: String, default: "" },
});

defineEmits([
  "refresh-locations",
  "select-location-card",
  "update:selected-location-preset",
  "update:location-search",
]);
</script>
