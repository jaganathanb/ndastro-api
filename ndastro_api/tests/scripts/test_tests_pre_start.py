from typing import NoReturn
from unittest.mock import MagicMock, patch

import pytest
import tenacity

tenacity.retry = lambda *a, **k: (lambda f: f)

from ndastro_api.tests_pre_start import init, main


@pytest.fixture
def mock_engine() -> MagicMock:
    return MagicMock()


def test_init_success(monkeypatch: pytest.MonkeyPatch, mock_engine: MagicMock) -> None:
    # Patch Session to not raise
    mock_session = MagicMock()
    mock_context = MagicMock()
    mock_session.__enter__.return_value = mock_context
    monkeypatch.setattr("ndastro_api.tests_pre_start.Session", lambda *a, **k: mock_session)
    monkeypatch.setattr("ndastro_api.tests_pre_start.select", lambda x: x)
    # Should not raise
    init(mock_engine)
    # Assert that __enter__ was called (context manager entered)
    mock_session.__enter__.assert_called_once()
    # Assert that exec was called on the context (session)
    mock_context.exec.assert_called()


class DBInitError(Exception):
    """Custom exception raised when database initialization fails.

    Args:
        engine (object): The database engine that caused the failure.

    """

    def __init__(self, engine: object) -> None:
        """Initialize DBInitError with the given engine."""
        msg = f"DB error initializing with engine: {engine}"
        super().__init__(msg)


def test_init_failure(monkeypatch: pytest.MonkeyPatch, mock_engine: MagicMock) -> None:
    # Patch Session to raise custom exception
    def raise_exc(*a, **k) -> NoReturn:
        raise DBInitError(mock_engine)

    mock_session = MagicMock()
    mock_session.__enter__.side_effect = raise_exc
    monkeypatch.setattr("ndastro_api.tests_pre_start.Session", lambda *a, **k: mock_session)
    with pytest.raises(DBInitError):
        init(mock_engine)


def test_main_logs(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch init to just log
    called = {}

    def fake_init(_: object) -> None:
        called["ran"] = True

    monkeypatch.setattr("ndastro_api.tests_pre_start.init", fake_init)
    with patch("ndastro_api.tests_pre_start.logger") as mock_logger:
        main()
        assert called["ran"]
        mock_logger.info.assert_any_call("Initializing service")
        mock_logger.info.assert_any_call("Service finished initializing")
