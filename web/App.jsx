import { useState, useEffect } from "react";
import "./css/App.css";
import ModelFilter from "./ModelFilter.jsx";
import HistoryListItem from "./HistoryListItem.jsx";
import { trainModel, listRuns, getRunPredictions } from "./api/prediction.js";
import { MODEL_FILTERS } from "./constants.js";
import { formatOneDecimal, getRowKey } from "./util.js";


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
  const [modelOutputs, setModelOutputs] = useState([]);

  useEffect(() => {
    const loadHistoryListOnStart = async () => {
      try {
        const runs = await listRuns(15);
        setLastRuns(runs);
      } catch (e) {
        throw new Error(`Error on startup: ${e.message}`);
      }
    }
    loadHistoryListOnStart();
  }, []);

  const handleHistoryListItemClick = async (run_uuid) => {
    try {
      const playerData = await getRunPredictions(run_uuid);
      setModelOutputs(playerData)
    } catch (e) {
      throw new Error(`Error when clicking history list item: ${e.message}`);
    }
  }

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
      // ignoring data because trainModel endpoint returns the latest run
      // but currently we do runs by position so you would only be returning
      // the more recent run and not all the positions in the specific "run"
      const data = await trainModel(payload);
      const runs = await listRuns(15);
      setLastRuns(runs);
    } catch (e) {
      setTrainError(e.message);
    } finally {
      setIsTraining(false);
    }
  };

  const parsedMinPred = Number.parseFloat(minPred);
  const parsedMinDelta = Number.parseFloat(minDelta);
  const minPredValue = Number.isNaN(parsedMinPred) ? 0 : parsedMinPred;
  const minDeltaValue = Number.isNaN(parsedMinDelta) ? 0 : parsedMinDelta;
  const filteredResults = modelOutputs.filter((row) => {
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

  const hasOutputs = modelOutputs.length > 0;
  const hasFilteredResults = filteredResults.length > 0;
  const isInitialEmptyState = !hasOutputs;

  const handleLoadLatestRun = async () => {
    if (lastRuns.length === 0) {
      return;
    }
    const latestRun = lastRuns[0];
    await handleHistoryListItemClick(latestRun.run_uuid);
  };

  const handleResetFilters = () => {
    setPositionFilter("All");
    setMinPred("0");
    setMinDelta("0");
  };

  return (
    <div className="base-container">
      <div className="filter-and-history-sidebar">
        <div className="sidebar-section">
          <div className="sidebar-title">Model Parameters</div>
          <div className="sidebar-subtitle">Fine-tune training inputs</div>
        </div>

        {MODEL_FILTERS.map((f) => (
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
              <HistoryListItem 
                key={prediction_run.run_uuid} 
                runData={prediction_run}
                handleClick={handleHistoryListItemClick}
              />
            ))}
          </div>
          <div className="history-footer">
            {trainError ? <div className="history-time">{trainError}</div> : null}
            <button
              className="train-button"
              type="button"
              onClick={handleTrain}
              disabled={isTraining}
            >
              {isTraining ? "Training..." : "Train Model"}
            </button>
          </div>
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
            <div className="results-table-output-container scroll-container">
              {hasFilteredResults ? (
                filteredResults.map((row, index) => (
                  <div key={getRowKey(row, index)} className="results-row">
                    <div className="player-cell">{row.full_name}</div>
                    <div>{row.team}</div>
                    <div>{row.position}</div>
                    <div>{formatOneDecimal(row.pred_next4)}</div>
                    <div className={row.delta >= 0 ? "delta up" : "delta down"}>
                      {formatOneDecimal(row.delta)}
                    </div>
                    <div>{formatOneDecimal(row.fantasy_prev_5wk_avg)}</div>
                  </div>
                ))
              ) : (
                <div className="results-empty-state">
                  {isInitialEmptyState ? (
                    <>
                      <div className="empty-title">No predictions yet</div>
                      <div className="empty-body">
                        Select a run from Training History or train a new model.
                      </div>
                      <div className="empty-actions">
                        <button
                          className="empty-button primary"
                          type="button"
                          onClick={handleLoadLatestRun}
                          disabled={lastRuns.length === 0 || isTraining}
                        >
                          Load latest run
                        </button>
                        <button
                          className="empty-button secondary"
                          type="button"
                          onClick={handleTrain}
                          disabled={isTraining}
                        >
                          {isTraining ? "Training..." : "Train model"}
                        </button>
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="empty-title">No results match these filters</div>
                      <div className="empty-body">
                        Try resetting filters or loosening your thresholds.
                      </div>
                      <div className="empty-actions">
                        <button
                          className="empty-button secondary"
                          type="button"
                          onClick={handleResetFilters}
                        >
                          Reset filters
                        </button>
                      </div>
                    </>
                  )}
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="results-grid">
            {filteredResults.map((row, index) => (
              <div key={getRowKey(row, index)} className="result-card">
                <div className="card-header">
                  <div className="card-name">{row.full_name}</div>
                  <div className="card-meta">
                    {row.team} - {row.position}
                  </div>
                </div>
                <div className="card-stats">
                  <div>
                    <div className="stat-label">pred_next4</div>
                    <div className="stat-value">{formatOneDecimal(row.pred_next4)}</div>
                  </div>
                  <div>
                    <div className="stat-label">delta</div>
                    <div className={`stat-value ${row.delta >= 0 ? "up" : "down"}`}>
                      {formatOneDecimal(row.delta)}
                    </div>
                  </div>
                  <div>
                    <div className="stat-label">prev_5wk_avg</div>
                    <div className="stat-value">
                      {formatOneDecimal(row.fantasy_prev_5wk_avg)}
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
