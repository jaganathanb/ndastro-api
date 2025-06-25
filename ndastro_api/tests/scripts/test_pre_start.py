from typing import NoReturn
from unittest.mock import MagicMock, patch

import pytest

# Patch tenacity.retry to a no-op decorator BEFORE importing the module under test
import tenacity

tenacity.retry = lambda *a, **k: (lambda f: f)

from ndastro_api.pre_start import init, main


def test_main_calls_init_and_logs() -> None:
    with patch("ndastro_api.pre_start.init") as mock_init, patch("ndastro_api.pre_start.logger") as mock_logger:
        main()
        mock_init.assert_called_once()
        mock_logger.info.assert_any_call("Initializing service")
        mock_logger.info.assert_any_call("Service finished initializing")


def test_init_success(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_engine = MagicMock()
    mock_session = MagicMock()
    mock_context = MagicMock()
    mock_session.__enter__.return_value = mock_context
    mock_session.__exit__.return_value = None  # Properly mock __exit__ as a method, not a MagicMock
    monkeypatch.setattr("ndastro_api.pre_start.Session", lambda *a, **k: mock_session)
    monkeypatch.setattr("ndastro_api.pre_start.select", lambda x: x)
    # Should not raise
    init(mock_engine)
    # Assert that __enter__ was called (context manager entered)
    mock_session.__enter__.assert_called_once()
    # Assert that exec was called on the context (session)
    mock_context.exec.assert_called()


def test_init_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_engine = MagicMock()

    class DummyError(Exception):
        pass

    def raise_exc() -> NoReturn:
        msg = "fail"
        raise DummyError(msg)

    mock_session = MagicMock()
    mock_session.__enter__.side_effect = raise_exc
    monkeypatch.setattr("ndastro_api.pre_start.Session", lambda *a, **k: mock_session)

    with pytest.raises(DummyError):
        init(mock_engine)
