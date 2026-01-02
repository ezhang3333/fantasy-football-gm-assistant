from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
from model.gbt_regression import (
    IDENTIFIER_COLS,
    apply_median_imputer,
    load_final_dataset,
    load_trained_xgb,
    latest_week_slice,
    score_candidates,
)


def _parse_positions(value: str) -> list[str]:
    positions = [p.strip().upper() for p in value.split(",") if p.strip()]
    return positions


def main() -> None:
    parser = argparse.ArgumentParser(description="Predict next-4-week average fantasy points and rank candidates.")
    parser.add_argument("--positions", default="QB,RB,WR,TE", help="Comma-separated: QB,RB,WR,TE")
    parser.add_argument("--data-dir", default="pipeline_data/final", help="Path to finalized CSVs")
    parser.add_argument("--model-dir", default="model/artifacts", help="Where models/metadata live")
    parser.add_argument("--out-dir", default="model/outputs", help="Where to write prediction CSVs")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for position in _parse_positions(args.positions):
        df = load_final_dataset(args.data_dir, position)
        season, week, df_latest = latest_week_slice(df)

        model, metadata = load_trained_xgb(args.model_dir, position)
        feature_cols = metadata["feature_cols"]
        medians = metadata["medians"]

        x = df_latest.loc[:, feature_cols].copy()
        for c in x.columns:
            x[c] = pd.to_numeric(x[c], errors="coerce")
        x = apply_median_imputer(x, medians)

        df_latest = df_latest.copy()
        df_latest["pred_next4"] = model.predict(x)
        scored = score_candidates(df_latest, position)

        base_cols = [c for c in IDENTIFIER_COLS if c in scored.columns]
        out_cols = base_cols + ["pred_next4", "delta"]
        out_cols = [c for c in out_cols if c in scored.columns]

        out_path = out_dir / f"{position.lower()}_predictions_{season}_wk{week}.csv"
        scored.sort_values("pred_next4", ascending=False)[out_cols].to_csv(out_path, index=False)


if __name__ == "__main__":
    main()

