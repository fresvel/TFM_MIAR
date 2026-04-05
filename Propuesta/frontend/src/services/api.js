import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8010";

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 20000,
});

export async function fetchMetadata() {
  const { data } = await client.get("/api/v1/metadata");
  return data;
}

export async function evaluateModule(payload) {
  const { data } = await client.post("/api/v1/evaluate", payload);
  return data;
}

export async function checkHealth() {
  const { data } = await client.get("/health");
  return data;
}

export async function fetchLocations(params = {}) {
  const { data } = await client.get("/api/v1/locations", { params });
  return data;
}

export async function fetchLocationSensors(locationId) {
  const { data } = await client.get(`/api/v1/locations/${locationId}/sensors`);
  return data;
}

export async function fetchHistory() {
  const { data } = await client.get("/api/v1/history");
  return data;
}

export async function fetchScenarios() {
  const { data } = await client.get("/api/v1/scenarios");
  return data;
}
