import os
import tempfile
from unittest.mock import patch
from fastapi.testclient import TestClient
from app import main

def test_llm_benchmark_with_mock_provider():
    with tempfile.TemporaryDirectory() as tmp:
        main.DB_PATH = os.path.join(tmp, "llm.db")
        with patch.object(main, "run_chat_completion", return_value="four") as provider:
            with TestClient(main.app) as client:
                response = client.post("/experiments", json={
                    "name": "mocked-llm", "strategy": "llm", "model": "test-model",
                    "cases": [{"prompt": "2 + 2 in words", "expected": "four"}]
                })
                assert response.status_code == 200
                assert response.json()["accuracy"] == 1.0
                provider.assert_called_once_with("2 + 2 in words", "test-model")

def test_llm_requires_model():
    with tempfile.TemporaryDirectory() as tmp:
        main.DB_PATH = os.path.join(tmp, "llm.db")
        with TestClient(main.app) as client:
            response = client.post("/experiments", json={
                "name": "missing-model", "strategy": "llm",
                "cases": [{"prompt": "hi", "expected": "hi"}]
            })
            assert response.status_code == 422
