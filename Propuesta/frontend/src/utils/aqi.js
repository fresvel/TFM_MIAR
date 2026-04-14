export function classifyAqiBand(value) {
  if (value <= 50) {
    return "good";
  }
  if (value <= 100) {
    return "moderate";
  }
  if (value <= 150) {
    return "unhealthy_sensitive_groups";
  }
  if (value <= 200) {
    return "unhealthy";
  }
  if (value <= 300) {
    return "very_unhealthy";
  }
  return "hazardous";
}

export function aqiBandColor(value, isDominant = false) {
  const paletteByBand = {
    good: isDominant ? "#2c9a47" : "#83cf7a",
    moderate: isDominant ? "#c47d13" : "#e5b85f",
    unhealthy_sensitive_groups: isDominant ? "#cf6447" : "#ef9d86",
    unhealthy: isDominant ? "#9a3412" : "#c96b4f",
    very_unhealthy: isDominant ? "#5b2c83" : "#8d63b0",
    hazardous: isDominant ? "#202738" : "#4d556b",
  };
  return paletteByBand[classifyAqiBand(value)];
}
