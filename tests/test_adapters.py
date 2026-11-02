from unittest.mock import patch
import pytest
from app.adapters import run_chat_completion

def test_requires_api_key():
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
            run_chat_completion("hello", "example-model")
