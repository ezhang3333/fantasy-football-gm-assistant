from __future__ import annotations
from dataclasses import asdict
from enum import Enum
from functools import lru_cache
from pathlib import Path
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from model.database import PredictionStore
from model.gbt_regression import XGBHyperParams, load_final_dataset, train_xgb_regressor
from model.predict import _default_output_columns, predict_position
from constants import DB_PATH


class Position(str, Enum):
    QB = "QB"
    RB = "RB"
    WR = "WR"
    TE = "TE"

app = FastAPI(title="FantasyFootball Predictions API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://localhost:3000",
    ],
    allow_methods=["*"],
    allow_headers=["*"]
)


@lru_cache(maxsize=1)
def _store() -> PredictionStore:
    db_path = DB_PATH
    store = PredictionStore(db_path)
    store.ensure_schema()
    return store


def get_store() -> PredictionStore:
    return _store()


class TrainRequest(BaseModel):
    positions: list[Position] = Field(default_factory=lambda: [Position.QB, Position.RB, Position.WR, Position.TE])
    data_dir: str = "pipeline_data/final"
    model_dir: str = "model/artifacts"
    val_season: int | None = None
    n_estimators: int = Field(default=300, ge=1)
    learning_rate: float = Field(default=0.1, gt=0, le=1)
    max_depth: int = Field(default=6, ge=1)
    subsample: float = Field(default=0.8, gt=0, le=1)
    colsample_bytree: float = Field(default=0.8, gt=0, le=1)
    reg_lambda: float = Field(default=1.0, ge=0)
    reg_alpha: float = Field(default=0.0, ge=0)


@app.get("/predictions/top")
async def get_top_predictions(
    position: Position,
    season: int | None = None,
    week: int | None = None,
    limit: int = Query(default=25, ge=1, le=500),
    store: PredictionStore = Depends(get_store),
):
    return store.get_top_predictions(position=position.value, season=season, week=week, limit=limit)


@app.get("/predictions/runs/list")
async def get_list_of_runs(
    limit: int = 15,
    store: PredictionStore = Depends(get_store),
):
    return store.get_past_runs_for_history_list(limit=limit)


@app.get("/predictions/runs/{run_uuid}")
async def get_predictions_for_run(run_uuid: str, store: PredictionStore = Depends(get_store)):
    return store.get_predictions(run_uuid=run_uuid)


@app.get("/predictions/batch/past")
async def get_past_batch_predictions(limit: int, store: PredictionStore = Depends(get_store)):
    return store.get_past_batch_predictions(limit)


@app.get("/predictions/batch/{batch_uuid}")
async def get_batch_prediction(batch_uuid: str, store: PredictionStore = Depends(get_store)):
    return store.get_batch_prediction(batch_uuid)


@app.get("/predictions/latest/{position}")
async def get_latest_predictions(position: Position, store: PredictionStore = Depends(get_store)):
    run = store.get_latest_run(position=position.value)
    if run is None:
        raise HTTPException(status_code=404, detail=f"No runs found for position={position.value}")
    return store.get_predictions(run_uuid=run.run_uuid)


@app.post("/train")
async def train_models(payload: TrainRequest, store: PredictionStore = Depends(get_store)):
    params = XGBHyperParams(
        n_estimators=payload.n_estimators,
        learning_rate=payload.learning_rate,
        max_depth=payload.max_depth,
        subsample=payload.subsample,
        colsample_bytree=payload.colsample_bytree,
        reg_lambda=payload.reg_lambda,
        reg_alpha=payload.reg_alpha,
    )

    batch_uuid = store.create_batch(
        data_dir=str(payload.data_dir),
        model_dir=str(payload.model_dir)
    )

    for position in payload.positions:
        df = load_final_dataset(payload.data_dir, position.value)
        train_xgb_regressor(
            position.value,
            df,
            payload.model_dir,
            val_season=payload.val_season,
            params=params,
        )

        result = predict_position(position.value, data_dir=payload.data_dir, model_dir=payload.model_dir)
        run_uuid = store.create_run(
            batch_uuid=batch_uuid,
            position=position.value,
            season=result.season,
            week=result.week,
            data_dir=str(payload.data_dir),
            model_dir=str(payload.model_dir),
            meta={**result.model_metadata, "train_params": asdict(params)},
        )
        store.save_predictions(run_uuid, batch_uuid, result.scored, payload_cols=_default_output_columns(result.scored))
    
    return store.get_batch_prediction(batch_uuid)
