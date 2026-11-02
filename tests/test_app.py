import os
import tempfile
from fastapi.testclient import TestClient
from app import main

def test_experiment_round_trip():
    with tempfile.TemporaryDirectory() as tmp:
        main.DB_PATH = os.path.join(tmp, "test.db")
        with TestClient(main.app) as client:
            response = client.post("/experiments", json={
                "name": "demo", "strategy": "echo",
                "cases": [{"prompt": "hello", "expected": "hello"},
                          {"prompt": "world", "expected": "different"}]
            })
            assert response.status_code == 200
            data = response.json()
            assert data["accuracy"] == 0.5
            assert len(client.get("/experiments").json()) == 1
            assert client.get(f"/experiments/{data['id']}").json()["name"] == "demo"

def test_invalid_strategy():
    with tempfile.TemporaryDirectory() as tmp:
        main.DB_PATH = os.path.join(tmp, "test.db")
        with TestClient(main.app) as client:
            assert client.post("/experiments", json={
                "name": "invalid", "strategy": "unknown",
                "cases": [{"prompt": "hi", "expected": "hi"}]
            }).status_code == 400
