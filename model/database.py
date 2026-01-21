from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Iterator, Mapping, Sequence
from uuid import uuid4


SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS prediction_runs (
  run_uuid TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  position TEXT NOT NULL,
  season INTEGER,
  week INTEGER,
  data_dir TEXT,
  model_dir TEXT,
  meta_json TEXT
);

CREATE TABLE IF NOT EXISTS predictions (
  prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_uuid TEXT NOT NULL,
  team TEXT,
  position TEXT,
  full_name TEXT,
  gsis_id TEXT,
  season INTEGER,
  week INTEGER,
  years_exp REAL,
  draft_number INTEGER,
  is_rookie INTEGER,
  is_second_year INTEGER,
  is_undrafted INTEGER,
  percent_rostered REAL,
  pred_next4 REAL,
  delta REAL,
  row_json TEXT,
  FOREIGN KEY (run_uuid) REFERENCES prediction_runs(run_uuid) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_predictions_run_uuid ON predictions(run_uuid);
CREATE INDEX IF NOT EXISTS idx_predictions_position_season_week ON predictions(position, season, week);
"""


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _is_nullish(value: Any) -> bool:
    try:
        if value is None:
            return True
        if isinstance(value, float) and value != value:
            return True
    except Exception:
        pass
    return False


def _jsonable(value: Any) -> Any:
    if _is_nullish(value):
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    try:
        # numpy scalar / pandas scalar
        item = getattr(value, "item", None)
        if callable(item):
            return _jsonable(item())
    except Exception:
        pass
    return str(value)


def _to_records(rows: Any) -> list[Mapping[str, Any]]:
    try:
        import pandas as pd  # type: ignore

        if isinstance(rows, pd.DataFrame):
            return list(rows.to_dict(orient="records"))
    except Exception:
        pass

    if isinstance(rows, Sequence):
        return list(rows)  # type: ignore[return-value]

    raise TypeError("rows must be a pandas DataFrame or a sequence of dict-like records")


def _existing_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    cols = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return {str(c[1]) for c in cols}


def _ensure_columns(conn: sqlite3.Connection, table: str, columns: Mapping[str, str]) -> None:
    existing = _existing_columns(conn, table)
    for name, col_type in columns.items():
        if name in existing:
            continue
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {col_type}")


def _to_int01(value: Any) -> int | None:
    if _is_nullish(value):
        return None
    if isinstance(value, bool):
        return 1 if value else 0
    try:
        return 1 if int(value) != 0 else 0
    except Exception:
        return None


def _to_float(value: Any) -> float | None:
    if _is_nullish(value):
        return None
    try:
        item = getattr(value, "item", None)
        if callable(item):
            value = item()
    except Exception:
        pass
    try:
        return float(value)
    except Exception:
        return None


def _to_int(value: Any) -> int | None:
    if _is_nullish(value):
        return None
    try:
        item = getattr(value, "item", None)
        if callable(item):
            value = item()
    except Exception:
        pass
    try:
        return int(value)
    except Exception:
        return None


@dataclass(frozen=True)
class PredictionRun:
    run_uuid: str
    created_at: str
    position: str
    season: int | None
    week: int | None
    data_dir: str | None
    model_dir: str | None
    meta: dict[str, Any]


class PredictionStore:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        try:
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            yield conn
            conn.commit()
        finally:
            conn.close()

    def ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(SCHEMA_SQL)
            _ensure_columns(
                conn,
                "predictions",
                {
                    "years_exp": "REAL",
                    "draft_number": "INTEGER",
                    "is_rookie": "INTEGER",
                    "is_second_year": "INTEGER",
                    "is_undrafted": "INTEGER",
                    "percent_rostered": "REAL",
                },
            )

    def create_run(
        self,
        *,
        position: str,
        season: int | None,
        week: int | None,
        data_dir: str | None = None,
        model_dir: str | None = None,
        meta: Mapping[str, Any] | None = None,
    ) -> str:
        run_uuid = uuid4().hex
        created_at = _utc_now_iso()
        meta_json = json.dumps(_jsonable(dict(meta or {})))

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO prediction_runs (run_uuid, created_at, position, season, week, data_dir, model_dir, meta_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (run_uuid, created_at, position, season, week, data_dir, model_dir, meta_json),
            )
        return run_uuid

    def save_predictions(
        self,
        run_uuid: str,
        rows: Any,
        *,
        payload_cols: Sequence[str] | None = None,
    ) -> int:
        records = _to_records(rows)

        def pick_payload(rec: Mapping[str, Any]) -> dict[str, Any]:
            if not payload_cols:
                return dict(rec)
            return {c: rec.get(c) for c in payload_cols if c in rec}

        to_insert: list[tuple[Any, ...]] = []
        for rec in records:
            team = rec.get("team")
            position = rec.get("position")
            full_name = rec.get("full_name")
            gsis_id = rec.get("gsis_id")
            season = rec.get("season")
            week = rec.get("week")
            years_exp = rec.get("years_exp_filled", rec.get("years_exp"))
            draft_number = rec.get("draft_number_filled", rec.get("draft_number"))
            is_rookie = rec.get("is_rookie")
            is_second_year = rec.get("is_second_year")
            is_undrafted = rec.get("is_undrafted")
            percent_rostered = rec.get("percent_rostered")
            pred_next4 = rec.get("pred_next4")
            delta = rec.get("delta")
            row_json = json.dumps(_jsonable(pick_payload(rec)))

            to_insert.append(
                (
                    run_uuid,
                    None if _is_nullish(team) else str(team),
                    None if _is_nullish(position) else str(position),
                    None if _is_nullish(full_name) else str(full_name),
                    None if _is_nullish(gsis_id) else str(gsis_id),
                    _to_int(season),
                    _to_int(week),
                    _to_float(years_exp),
                    _to_int(draft_number),
                    _to_int01(is_rookie),
                    _to_int01(is_second_year),
                    _to_int01(is_undrafted),
                    _to_float(percent_rostered),
                    _to_float(pred_next4),
                    _to_float(delta),
                    row_json,
                )
            )

        with self._connect() as conn:
            cur = conn.executemany(
                """
                INSERT INTO predictions (
                  run_uuid, team, position, full_name, gsis_id, season, week,
                  years_exp, draft_number, is_rookie, is_second_year, is_undrafted, percent_rostered,
                  pred_next4, delta, row_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?,
                        ?, ?, ?)
                """,
                to_insert,
            )
            return int(cur.rowcount or 0)

    def get_latest_run(self, *, position: str | None = None) -> PredictionRun | None:
        with self._connect() as conn:
            if position:
                row = conn.execute(
                    """
                    SELECT run_uuid, created_at, position, season, week, data_dir, model_dir, meta_json
                    FROM prediction_runs
                    WHERE position = ?
                    ORDER BY created_at DESC
                    LIMIT 1
                    """,
                    (position,),
                ).fetchone()
            else:
                row = conn.execute(
                    """
                    SELECT run_uuid, created_at, position, season, week, data_dir, model_dir, meta_json
                    FROM prediction_runs
                    ORDER BY created_at DESC
                    LIMIT 1
                    """
                ).fetchone()

        if row is None:
            return None
        meta = {}
        try:
            meta = json.loads(row["meta_json"] or "{}")
        except Exception:
            meta = {}
        return PredictionRun(
            run_uuid=str(row["run_uuid"]),
            created_at=str(row["created_at"]),
            position=str(row["position"]),
            season=None if row["season"] is None else int(row["season"]),
            week=None if row["week"] is None else int(row["week"]),
            data_dir=None if row["data_dir"] is None else str(row["data_dir"]),
            model_dir=None if row["model_dir"] is None else str(row["model_dir"]),
            meta=meta,
        )
    
    def get_past_runs_for_history_list(self, *, limit: int = 50):
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT run_uuid, created_at, position, season
                FROM prediction_runs
                ORDER BY created_at DESC
                LIMIT :limit
                """,
                {"limit": int(limit)},
            ).fetchall()

        return [dict(r) for r in rows]
        

    def get_predictions(self, *, run_uuid: str, limit: int | None = None) -> list[dict[str, Any]]:
        limit_sql = "" if limit is None else "LIMIT ?"
        params: tuple[Any, ...] = (run_uuid,) if limit is None else (run_uuid, int(limit))

        with self._connect() as conn:
            rows = conn.execute(
                f"""
                SELECT
                  team, position, full_name, gsis_id, season, week,
                  years_exp, draft_number, is_rookie, is_second_year, is_undrafted, percent_rostered,
                  pred_next4, delta, row_json
                FROM predictions
                WHERE run_uuid = ?
                ORDER BY pred_next4 DESC
                {limit_sql}
                """,
                params,
            ).fetchall()

        out: list[dict[str, Any]] = []
        for r in rows:
            base = dict(r)
            try:
                payload = json.loads(base.pop("row_json") or "{}")
            except Exception:
                payload = {}
            out.append({**base, **payload})
        return out

    def get_top_predictions(
        self,
        *,
        position: str,
        season: int | None = None,
        week: int | None = None,
        limit: int = 25,
    ) -> list[dict[str, Any]]:
        with self._connect() as conn:
            where = ["p.position = ?"]
            params: list[Any] = [position]
            if season is not None:
                where.append("p.season = ?")
                params.append(int(season))
            if week is not None:
                where.append("p.week = ?")
                params.append(int(week))

            rows = conn.execute(
                f"""
                SELECT
                  r.created_at, r.run_uuid,
                  p.team, p.position, p.full_name, p.gsis_id, p.season, p.week,
                  p.years_exp, p.draft_number, p.is_rookie, p.is_second_year, p.is_undrafted, p.percent_rostered,
                  p.pred_next4, p.delta
                FROM predictions p
                JOIN prediction_runs r ON r.run_uuid = p.run_uuid
                WHERE {" AND ".join(where)}
                ORDER BY r.created_at DESC, p.pred_next4 DESC
                LIMIT ?
                """,
                (*params, int(limit)),
            ).fetchall()

        return [dict(r) for r in rows]
