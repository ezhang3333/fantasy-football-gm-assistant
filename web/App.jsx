import { useState } from "react";
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

  const handleParamChange = (name, rawValue) => {
    setParams((prev) => ({ ...prev, [name]: rawValue }));
  };

  return (
    <div className="base-container">
      <div className="filter-and-history-sidebar">
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
      </div>

      <div className="output-container">
        <h3>Fantasy Football Predictor: Gradient Boosted Tree Model</h3>
      </div>
    </div>
  );
}
