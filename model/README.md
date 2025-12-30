# Models

This folder trains a per-position gradient-boosted tree **regression** model to predict `fantasy_next_4wk_avg`.

## Install

From your venv:

```powershell
pip install -r model/requirements.txt
```

Notes:
- This repo already uses `pandas`/`numpy` elsewhere; `model/requirements.txt` intentionally doesn’t pin them to avoid dependency conflicts.

## Train

Uses `pipeline_data/final/*_final_data.csv` and a time-based split (all seasons `< val_season` train, `val_season` validate).

```powershell
python -m model.train
```

Optional:

```powershell
python -m model.train --positions QB,RB --val-season 2025
```

Models + metadata are saved to `model/artifacts/<pos>/`.

## Predict + Rank

Predicts `pred_next4` for the latest week in the latest season and outputs candidate rankings.

```powershell
python -m model.predict
```

Outputs are written to `model/outputs/`.
