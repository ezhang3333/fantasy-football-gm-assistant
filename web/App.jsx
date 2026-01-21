import { useState, useEffect } from "react";
import "./css/App.css";
import ModelFilter from "./ModelFilter.jsx";

const FILTERS = [
  { name: "n_estimators", label: "n_estimators", min: 1, step: 1 },
  { name: "learning_rate", label: "learning_rate", min: 0, max: 1, step: 0.01 },
  { name: "max_depth", label: "max_depth", min: 1, step: 1 },
  { name: "subsample", label: "subsample", min: 0, max: 1, step: 0.01 },
  { name: "colsample_bytree", label: "colsample_bytree", min: 0, max: 1, step: 0.01 },
  { name: "reg_lambda", label: "reg_lambda", min: 0, step: 0.1 },
  { name: "reg_alpha", label: "reg_alpha", min: 0, step: 0.1 },
];


const MOCK_RESULTS = [
  {
    id: "p1",
    full_name: "Josh Allen",
    team: "BUF",
    position: "QB",
    pred_next4: 23.4,
    delta: 3.1,
    fantasy_prev_5wk_avg: 20.3,
  },
  {
    id: "p2",
    full_name: "Jahmyr Gibbs",
    team: "DET",
    position: "RB",
    pred_next4: 17.8,
    delta: 2.4,
    fantasy_prev_5wk_avg: 15.4,
  },
  {
    id: "p3",
    full_name: "CeeDee Lamb",
    team: "DAL",
    position: "WR",
    pred_next4: 18.9,
    delta: 1.2,
    fantasy_prev_5wk_avg: 17.7,
  },
  {
    id: "p4",
    full_name: "Sam LaPorta",
    team: "DET",
    position: "TE",
    pred_next4: 12.6,
    delta: -0.4,
    fantasy_prev_5wk_avg: 13.0,
  },
  {
    id: "p5",
    full_name: "Brock Purdy",
    team: "SF",
    position: "QB",
    pred_next4: 19.2,
    delta: 0.8,
    fantasy_prev_5wk_avg: 18.4,
  },
  {
    id: "p6",
    full_name: "Bijan Robinson",
    team: "ATL",
    position: "RB",
    pred_next4: 16.1,
    delta: -1.0,
    fantasy_prev_5wk_avg: 17.1,
  },
];

export default function App() {
  const [params, setParams] = useState({
    n_estimators: "300",
    learning_rate: "0.1",
    max_depth: "6",
    subsample: "0.8",
    colsample_bytree: "0.8",
    reg_lambda: "1",
    reg_alpha: "0",
  });
  const [isTraining, setIsTraining] = useState(false);
  const [trainError, setTrainError] = useState("");
  const [lastRuns, setLastRuns] = useState([]);
  const [viewMode, setViewMode] = useState("list");
  const [positionFilter, setPositionFilter] = useState("All");
  const [minPred, setMinPred] = useState("0");
  const [minDelta, setMinDelta] = useState("0");
  const apiBase = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

  useEffect(() => {
    const apiUrl = `${apiBase}/predictions/runs/latest`
    const fetchAPI = async () => {
      const response = await fetch(apiUrl)
      const data = await response.json()
      setLastRuns(data)
    }
    fetchAPI()
  }, [apiBase]);

  const handleParamChange = (name, rawValue) => {
    setParams((prev) => ({ ...prev, [name]: rawValue }));
  };

  const handleTrain = async () => {
    setIsTraining(true);
    setTrainError("");

    const payload = {
      positions: ["QB", "RB", "WR", "TE"],
      n_estimators: Number(params.n_estimators),
      learning_rate: Number(params.learning_rate),
      max_depth: Number(params.max_depth),
      subsample: Number(params.subsample),
      colsample_bytree: Number(params.colsample_bytree),
      reg_lambda: Number(params.reg_lambda),
      reg_alpha: Number(params.reg_alpha),
    };

    try {
      const response = await fetch(`${apiBase}/train`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        throw new Error(`Train failed (${response.status})`);
      }
      const data = await response.json();
      setLastRuns((prev) => [data, ...prev]);
    } catch (error) {
      setTrainError(error instanceof Error ? error.message : "Train failed");
    } finally {
      setIsTraining(false);
    }
  };

  const parsedMinPred = Number.parseFloat(minPred);
  const parsedMinDelta = Number.parseFloat(minDelta);
  const minPredValue = Number.isNaN(parsedMinPred) ? 0 : parsedMinPred;
  const minDeltaValue = Number.isNaN(parsedMinDelta) ? 0 : parsedMinDelta;
  const filteredResults = MOCK_RESULTS.filter((row) => {
    if (positionFilter !== "All" && row.position !== positionFilter) {
      return false;
    }
    if (row.pred_next4 < minPredValue) {
      return false;
    }
    if (row.delta < minDeltaValue) {
      return false;
    }
    return true;
  });

  return (
    <div className="base-container">
      <div className="filter-and-history-sidebar">
        <div className="sidebar-section">
          <div className="sidebar-title">Model Parameters</div>
          <div className="sidebar-subtitle">Fine-tune training inputs</div>
        </div>

        {FILTERS.map((f) => (
          <ModelFilter
            key={f.name}
            name={f.name}
            label={f.label}
            value={params[f.name]}
            onChange={handleParamChange}
            min={f.min}
            max={f.max}
            step={f.step}
          />
        ))}

        <div className="history-section">
          <div className="sidebar-title">Training History</div>
          <div className="history-list scroll-container">
            {lastRuns.map((prediction_run) => (
              <div key={prediction_run.run_uuid} className="history-row">
                <div className="history-label">LABEL</div>
                <div className="history-time">{prediction_run.created_at}</div>
              </div>
            ))}
          </div>
          <button
            className="train-button"
            type="button"
            onClick={handleTrain}
            disabled={isTraining}
          >
            {isTraining ? "Training..." : "Train Model"}
          </button>
          {trainError ? <div className="history-time">{trainError}</div> : null}
          {lastRuns.length > 0 ? (
            <div className="history-time">Latest run: {lastRuns[0].run_uuid}</div>
          ) : null}
        </div>
      </div>

      <div className="output-container">
        <div className="output-header">
          <div>
            <div className="output-title">Fantasy Football Predictor</div>
            <div className="output-subtitle">Gradient Boosted Tree Model</div>
          </div>
          <div className="view-toggle">
            <button
              className={`toggle-button ${viewMode === "list" ? "active" : ""}`}
              type="button"
              onClick={() => setViewMode("list")}
            >
              List
            </button>
            <button
              className={`toggle-button ${viewMode === "grid" ? "active" : ""}`}
              type="button"
              onClick={() => setViewMode("grid")}
            >
              Grid
            </button>
          </div>
        </div>

        <div className="output-filters">
          <div className="filter-group">
            <label className="filter-label" htmlFor="position-filter">
              Position
            </label>
            <select
              id="position-filter"
              className="filter-select"
              value={positionFilter}
              onChange={(e) => setPositionFilter(e.target.value)}
            >
              <option value="All">All</option>
              <option value="QB">QB</option>
              <option value="RB">RB</option>
              <option value="WR">WR</option>
              <option value ="TE">TE</option>
            </select>
          </div>
          <div className="filter-group">
            <label className="filter-label" htmlFor="min-pred">
              Min pred_next4
            </label>
            <input
              id="min-pred"
              className="filter-input"
              type="number"
              step="0.1"
              value={minPred}
              onChange={(e) => setMinPred(e.target.value)}
            />
          </div>
          <div className="filter-group">
            <label className="filter-label" htmlFor="min-delta">
              Min delta
            </label>
            <input
              id="min-delta"
              className="filter-input"
              type="number"
              step="0.1"
              value={minDelta}
              onChange={(e) => setMinDelta(e.target.value)}
            />
          </div>
        </div>

        {viewMode === "list" ? (
          <div className="results-table">
            <div className="results-row results-header">
              <div>Player</div>
              <div>Team</div>
              <div>Pos</div>
              <div>pred_next4</div>
              <div>delta</div>
              <div>prev_5wk_avg</div>
            </div>
            {filteredResults.map((row) => (
              <div key={row.id} className="results-row">
                <div className="player-cell">{row.full_name}</div>
                <div>{row.team}</div>
                <div>{row.position}</div>
                <div>{row.pred_next4.toFixed(1)}</div>
                <div className={row.delta >= 0 ? "delta up" : "delta down"}>
                  {row.delta.toFixed(1)}
                </div>
                <div>{row.fantasy_prev_5wk_avg.toFixed(1)}</div>
              </div>
            ))}
          </div>
        ) : (
          <div className="results-grid">
            {filteredResults.map((row) => (
              <div key={row.id} className="result-card">
                <div className="card-header">
                  <div className="card-name">{row.full_name}</div>
                  <div className="card-meta">
                    {row.team} - {row.position}
                  </div>
                </div>
                <div className="card-stats">
                  <div>
                    <div className="stat-label">pred_next4</div>
                    <div className="stat-value">{row.pred_next4.toFixed(1)}</div>
                  </div>
                  <div>
                    <div className="stat-label">delta</div>
                    <div className={`stat-value ${row.delta >= 0 ? "up" : "down"}`}>
                      {row.delta.toFixed(1)}
                    </div>
                  </div>
                  <div>
                    <div className="stat-label">prev_5wk_avg</div>
                    <div className="stat-value">
                      {row.fantasy_prev_5wk_avg.toFixed(1)}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
