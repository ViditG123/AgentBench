"""Local deterministic benchmark runner with SQLite experiment results."""
import json
import os
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

DB_PATH = os.getenv("AGENTBENCH_DB", "agentbench.db")
app = FastAPI(title="AgentBench", version="0.1.0")

@contextmanager
def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with db() as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS experiments (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, accuracy REAL NOT NULL, latency_ms REAL NOT NULL, results TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP)")

class Case(BaseModel):
    prompt: str = Field(min_length=1)
    expected: str

class RunRequest(BaseModel):
    name: str = Field(min_length=1)
    strategy: str = "echo"
    cases: list[Case] = Field(min_length=1)

def evaluate(strategy: str, prompt: str) -> str:
    if strategy == "echo":
        return prompt
    if strategy == "lowercase":
        return prompt.lower()
    if strategy == "reverse":
        return prompt[::-1]
    raise ValueError("Unsupported strategy")

@app.on_event("startup")
def startup():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    init_db()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/experiments")
def run_experiment(req: RunRequest):
    if req.strategy not in ("echo", "lowercase", "reverse"):
        raise HTTPException(status_code=400, detail="Unsupported strategy")
    results = []
    total_ms = 0.0
    for case in req.cases:
        started = time.perf_counter()
        actual = evaluate(req.strategy, case.prompt)
        elapsed = (time.perf_counter() - started) * 1000
        total_ms += elapsed
        results.append({"prompt": case.prompt, "expected": case.expected, "actual": actual, "passed": actual == case.expected, "latency_ms": elapsed})
    accuracy = sum(item["passed"] for item in results) / len(results)
    avg_latency = total_ms / len(results)
    with db() as conn:
        cursor = conn.execute("INSERT INTO experiments (name, accuracy, latency_ms, results) VALUES (?, ?, ?, ?)", (req.name, accuracy, avg_latency, json.dumps(results)))
        experiment_id = cursor.lastrowid
    return {"id": experiment_id, "name": req.name, "accuracy": accuracy, "avg_latency_ms": avg_latency, "results": results}

@app.get("/experiments")
def list_experiments():
    with db() as conn:
        rows = conn.execute("SELECT id, name, accuracy, latency_ms, created_at FROM experiments ORDER BY id DESC").fetchall()
    return [dict(row) for row in rows]

@app.get("/experiments/{experiment_id}")
def get_experiment(experiment_id: int):
    with db() as conn:
        row = conn.execute("SELECT * FROM experiments WHERE id=?", (experiment_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    result = dict(row)
    result["results"] = json.loads(result["results"])
    return result
