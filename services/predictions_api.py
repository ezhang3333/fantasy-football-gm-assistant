from fastapi import Depends, FastAPI
from model.database import PredictionStore

app = FastAPI()

def get_store() -> PredictionStore:
    store = PredictionStore("model/outputs/predictions.sqlite3")
    store.ensure_schema()
    return store

@app.get("/predictions/runs/{run_uuid}")
async def get_prediction_run(run_uuid: str, store: PredictionStore = Depends(get_store)):
    return store.get_predictions(run_uuid)