export function formatOneDecimal(value) {
  const num = Number(value);
  return Number.isFinite(num) ? num.toFixed(1) : "N/A";
}

export function getRowKey(row, index) {
  if (row.gsis_id) {
    return `${row.gsis_id}-${row.season ?? "s"}-${row.week ?? "w"}`;
  }
  return `${row.full_name ?? "player"}-${row.team ?? "team"}-${index}`;
}
