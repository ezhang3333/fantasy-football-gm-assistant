from __future__ import annotations

import argparse
from dataclasses import dataclass
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
    return [p.strip().upper() for p in value.split(",") if p.strip()]


@dataclass(frozen=True)
class PredictionResult:
    position: str
    season: int
    week: int
    scored: pd.DataFrame
    model_metadata: dict[str, object]


def predict_position(
    position: str,
    *,
    data_dir: str | Path = "pipeline_data/final",
    model_dir: str | Path = "model/artifacts",
) -> PredictionResult:
    df = load_final_dataset(data_dir, position)
    season, week, df_latest = latest_week_slice(df)

    model, metadata = load_trained_xgb(model_dir, position)
    feature_cols = list(metadata["feature_cols"])
    medians = dict(metadata["medians"])

    x = df_latest.loc[:, feature_cols].copy()
    for c in x.columns:
        x[c] = pd.to_numeric(x[c], errors="coerce")
    x = apply_median_imputer(x, medians)

    df_latest = df_latest.copy()
    df_latest["pred_next4"] = model.predict(x)
    scored = score_candidates(df_latest, position)

    model_metadata = {
        "position": position,
        "target_col": metadata.get("target_col"),
        "val_season": metadata.get("val_season"),
        "best_iteration": metadata.get("best_iteration"),
        "validation_metrics": metadata.get("validation_metrics"),
    }

    return PredictionResult(position=position, season=season, week=week, scored=scored, model_metadata=model_metadata)


def _default_output_columns(df: pd.DataFrame) -> list[str]:
    base_cols = [c for c in IDENTIFIER_COLS if c in df.columns]
    extras = [
        "years_exp",
        "years_exp_filled",
        "draft_number",
        "draft_number_filled",
        "is_rookie",
        "is_second_year",
        "is_undrafted",
        "percent_rostered",
        "fantasy_prev_5wk_avg",
    ]
    out_cols = base_cols + [c for c in extras if c in df.columns] + ["pred_next4", "delta"]
    return [c for c in out_cols if c in df.columns]


def write_predictions_csv(result: PredictionResult, *, out_dir: str | Path) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / f"{result.position.lower()}_predictions_{result.season}_wk{result.week}.csv"
    out_cols = _default_output_columns(result.scored)
    result.scored.sort_values("pred_next4", ascending=False)[out_cols].to_csv(out_path, index=False)
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Predict next-4-week average fantasy points and rank candidates.")
    parser.add_argument("--positions", default="QB,RB,WR,TE", help="Comma-separated: QB,RB,WR,TE")
    parser.add_argument("--data-dir", default="pipeline_data/final", help="Path to finalized CSVs")
    parser.add_argument("--model-dir", default="model/artifacts", help="Where models/metadata live")
    parser.add_argument("--out-dir", default="model/outputs", help="Where to write prediction CSVs")
    parser.add_argument("--write-db", action="store_true", help="Also store predictions in a SQLite database")
    parser.add_argument("--db-path", default="model/outputs/predictions.sqlite3", help="SQLite path for stored predictions")
    args = parser.parse_args()

    store = None
    if args.write_db:
        from model.database import PredictionStore

        store = PredictionStore(args.db_path)
        store.ensure_schema()

    for position in _parse_positions(args.positions):
        result = predict_position(position, data_dir=args.data_dir, model_dir=args.model_dir)
        out_path = write_predictions_csv(result, out_dir=args.out_dir)
        print(f"[{position}] wrote: {out_path}")

        if store is not None:
            run_uuid = store.create_run(
                position=position,
                season=result.season,
                week=result.week,
                data_dir=str(args.data_dir),
                model_dir=str(args.model_dir),
                meta=result.model_metadata,
            )
            store.save_predictions(run_uuid, result.scored, payload_cols=_default_output_columns(result.scored))
            print(f"[{position}] stored in db: {args.db_path} (run={run_uuid})")


if __name__ == "__main__":
    main()
