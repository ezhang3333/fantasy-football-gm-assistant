export const MODEL_FILTERS = [
  { name: "n_estimators", label: "n_estimators", min: 1, step: 1 },
  { name: "learning_rate", label: "learning_rate", min: 0, max: 1, step: 0.01 },
  { name: "max_depth", label: "max_depth", min: 1, step: 1 },
  { name: "subsample", label: "subsample", min: 0, max: 1, step: 0.01 },
  { name: "colsample_bytree", label: "colsample_bytree", min: 0, max: 1, step: 0.01 },
  { name: "reg_lambda", label: "reg_lambda", min: 0, step: 0.1 },
  { name: "reg_alpha", label: "reg_alpha", min: 0, step: 0.1 },
];