from __future__ import annotations
from enum import Enum
from functools import lru_cache
from pathlib import Path
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from model.database import PredictionStore

class Position(str, Enum):
    QB = "QB"
    RB = "RB"
    WR = "WR"
    TE = "TE"

app = FastAPI(title="FantasyFootball Predictions API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"]
)


@lru_cache(maxsize=1)
def _store() -> PredictionStore:
    store = PredictionStore("model/outputs/predictions.sqlite3")
    store.ensure_schema()
    return store


def get_store() -> PredictionStore:
    return _store()


@app.get("/predictions/runs/{run_uuid}")
async def get_predictions_for_run(run_uuid: str, store: PredictionStore = Depends(get_store)):
    return store.get_predictions(run_uuid=run_uuid)


@app.get("/predictions/top")
async def get_top_predictions(
    position: Position,
    season: int | None = None,
    week: int | None = None,
    limit: int = Query(default=25, ge=1, le=500),
    store: PredictionStore = Depends(get_store),
):
    return store.get_top_predictions(position=position.value, season=season, week=week, limit=limit)


@app.get("/predictions/latest/{position}")
async def get_latest_predictions(position: Position, store: PredictionStore = Depends(get_store)):
    run = store.get_latest_run(position=position.value)
    if run is None:
        raise HTTPException(status_code=404, detail=f"No runs found for position={position.value}")
    return store.get_predictions(run_uuid=run.run_uuid)
