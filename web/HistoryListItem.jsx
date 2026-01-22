function timeAgo(isoString) {
  const then = new Date(isoString).getTime();
  if (Number.isNaN(then)) return "unknown";
  const seconds = Math.floor((Date.now() - then) / 1000);

  const units = [
    ["day", 86400],
    ["hour", 3600],
    ["minute", 60],
    ["second", 1],
  ];

  for (const [name, secs] of units) {
    if (seconds >= secs) {
      const value = Math.floor(seconds / secs);
      return `${value} ${name}${value !== 1 ? "s" : ""} ago`;
    }
  }
  return "just now";
}

export default function HistoryListItem({ runData }) {
    const label = `${runData.position} - Validated on ${runData.season} - ${timeAgo(runData.created_at)}`
    return (
        <div className="history-row">
            <div className="history-label">{label}</div>
        </div>
    );
}