from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from model.gbt_regression import (
    apply_median_imputer,
    load_final_dataset,
    load_trained_xgb,
    regression_metrics,
    time_split_by_season,
    _to_numeric_frame,
)


try:
    from scipy.stats import spearmanr  # type: ignore[import-not-found]
except Exception:  # pragma: no cover
    spearmanr = None

try:
    from sklearn.metrics import roc_auc_score  # type: ignore[import-not-found]
except Exception:  # pragma: no cover
    roc_auc_score = None


TOPK_BY_POSITION: dict[str, int] = {"QB": 12, "RB": 24, "WR": 24, "TE": 12}


def _parse_positions(value: str) -> list[str]:
    return [p.strip().upper() for p in value.split(",") if p.strip()]


def _spearman(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    mask = ~np.isnan(a) & ~np.isnan(b)
    a = a[mask]
    b = b[mask]
    if a.size < 3:
        return float("nan")
    if spearmanr is not None:
        return float(spearmanr(a, b).correlation)
    return float(pd.Series(a).rank().corr(pd.Series(b).rank()))


def _precision_at_k_weekly(df: pd.DataFrame, *, y_col: str, pred_col: str, k: int) -> tuple[float, int]:
    if "week" not in df.columns:
        return float("nan"), 0
    precisions: list[float] = []
    for _, g in df.groupby("week"):
        if len(g) < k:
            continue
        top_true = set(g.sort_values(y_col, ascending=False).head(k).index)
        top_pred = set(g.sort_values(pred_col, ascending=False).head(k).index)
        precisions.append(len(top_true & top_pred) / k)
    return (float(np.mean(precisions)) if precisions else float("nan")), int(len(precisions))


@dataclass(frozen=True)
class EvalResult:
    position: str
    val_season: int
    n: int
    model: dict[str, float]
    baselines: dict[str, dict[str, float]]
    precision_at_k_weekly_mean: float
    precision_at_k_weeks: int
    delta_vs_prev5: dict[str, float] | None
    breakout_auc: float | None

    def to_dict(self) -> dict[str, object]:
        return {
            "position": self.position,
            "val_season": self.val_season,
            "n": self.n,
            "model": self.model,
            "baselines": self.baselines,
            "precision_at_k_weekly_mean": self.precision_at_k_weekly_mean,
            "precision_at_k_weeks": self.precision_at_k_weeks,
            "delta_vs_prev5": self.delta_vs_prev5,
            "breakout_auc": self.breakout_auc,
        }


def evaluate_position(
    position: str,
    *,
    data_dir: str | Path,
    model_dir: str | Path,
    val_season: int | None,
    breakout_threshold: float,
) -> EvalResult:
    model, meta = load_trained_xgb(model_dir, position)
    feature_cols = list(meta["feature_cols"])
    medians = dict(meta["medians"])
    target_col = str(meta["target_col"])
    meta_val_season = int(meta["val_season"])
    val_season = meta_val_season if val_season is None else int(val_season)

    df = load_final_dataset(data_dir, position)
    _, val_df, _ = time_split_by_season(df, val_season=val_season)

    y = pd.to_numeric(val_df[target_col], errors="coerce")
    mask = ~y.isna()
    val_df = val_df.loc[mask].copy()
    y = y.loc[mask].astype(float)

    x = _to_numeric_frame(val_df, feature_cols)
    x = apply_median_imputer(x, medians)
    pred = pd.Series(model.predict(x), index=val_df.index, dtype=float)

    model_metrics = {
        **regression_metrics(y.to_numpy(), pred.to_numpy()),
        "spearman": _spearman(y.to_numpy(), pred.to_numpy()),
    }

    baseline_cols = [c for c in ["fantasy_prev_5wk_avg", "fantasy_3wk_avg", "fantasy_ppr_3wk_avg"] if c in val_df.columns]
    baselines: dict[str, dict[str, float]] = {}
    for c in baseline_cols:
        b = pd.to_numeric(val_df[c], errors="coerce").astype(float)
        bmask = ~b.isna()
        yy = y.loc[bmask]
        bb = b.loc[bmask]
        baselines[c] = {
            **regression_metrics(yy.to_numpy(), bb.to_numpy()),
            "spearman": _spearman(yy.to_numpy(), bb.to_numpy()),
            "n": float(int(bmask.sum())),
        }

    val_df = val_df.assign(_y=y, _pred=pred)
    k = TOPK_BY_POSITION.get(position, 12)
    prec, n_weeks = _precision_at_k_weekly(val_df, y_col="_y", pred_col="_pred", k=k)

    delta_vs_prev5: dict[str, float] | None = None
    breakout_auc: float | None = None
    if "fantasy_prev_5wk_avg" in val_df.columns:
        prev5 = pd.to_numeric(val_df["fantasy_prev_5wk_avg"], errors="coerce").astype(float)
        pmask = ~prev5.isna()
        delta_true = (y - prev5).loc[pmask].to_numpy(dtype=float)
        delta_pred = (pred - prev5).loc[pmask].to_numpy(dtype=float)
        delta_vs_prev5 = {
            "spearman": _spearman(delta_true, delta_pred),
            "pearson": float(pd.Series(delta_true).corr(pd.Series(delta_pred))),
            "n": float(int(pmask.sum())),
        }

        label = (delta_true >= breakout_threshold).astype(int)
        if roc_auc_score is not None and len(np.unique(label)) == 2:
            breakout_auc = float(roc_auc_score(label, delta_pred))

    return EvalResult(
        position=position,
        val_season=val_season,
        n=int(len(val_df)),
        model=model_metrics,
        baselines=baselines,
        precision_at_k_weekly_mean=prec,
        precision_at_k_weeks=n_weeks,
        delta_vs_prev5=delta_vs_prev5,
        breakout_auc=breakout_auc,
    )


def _format_float(v: float | None) -> str:
    if v is None:
        return "-"
    if isinstance(v, float) and np.isnan(v):
        return "nan"
    return f"{v:.3f}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate per-position XGBoost models on the validation season.")
    parser.add_argument("--positions", default="QB,RB,WR,TE", help="Comma-separated: QB,RB,WR,TE")
    parser.add_argument("--data-dir", default="pipeline_data/final", help="Path to finalized CSVs")
    parser.add_argument("--model-dir", default="model/artifacts", help="Where models/metadata live")
    parser.add_argument("--val-season", type=int, default=None, help="Override val season (default: from metadata)")
    parser.add_argument("--breakout-threshold", type=float, default=3.0, help="Delta threshold vs prev5 for breakout label")
    parser.add_argument("--out", default=None, help="Optional path to write JSON results")
    args = parser.parse_args()

    results = [
        evaluate_position(
            p,
            data_dir=args.data_dir,
            model_dir=args.model_dir,
            val_season=args.val_season,
            breakout_threshold=args.breakout_threshold,
        ).to_dict()
        for p in _parse_positions(args.positions)
    ]

    df = pd.DataFrame(
        [
            {
                "pos": r["position"],
                "val": r["val_season"],
                "n": r["n"],
                "mae": r["model"]["mae"],
                "rmse": r["model"]["rmse"],
                "r2": r["model"]["r2"],
                "spearman": r["model"]["spearman"],
                "p@k_weekly": r["precision_at_k_weekly_mean"],
                "breakout_auc": None if r["breakout_auc"] is None else r["breakout_auc"],
            }
            for r in results
        ]
    ).sort_values("pos")

    print(df.to_string(index=False, formatters={c: _format_float for c in ["mae", "rmse", "r2", "spearman", "p@k_weekly", "breakout_auc"]}))

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(f"\nWrote: {out_path}")


if __name__ == "__main__":
    main()

