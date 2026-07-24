"""Unit tests for operators/main.py's request_with_retry -- the retry/
backoff logic behind every Spotify API call this pipeline makes."""
from unittest.mock import MagicMock, patch

import requests

from main import request_with_retry


def _response(status_code):
    resp = MagicMock()
    resp.status_code = status_code
    return resp


@patch("main.time.sleep")
@patch("main.requests.get")
def test_returns_immediately_on_success(mock_get, mock_sleep):
    mock_get.return_value = _response(200)

    response = request_with_retry("http://example.com", headers={})

    assert response.status_code == 200
    assert mock_get.call_count == 1
    mock_sleep.assert_not_called()


@patch("main.time.sleep")
@patch("main.requests.get")
def test_client_error_returns_immediately_without_retrying(mock_get, mock_sleep):
    """A 401/403 fails identically on every attempt -- retrying just delays
    the caller's existing fail-fast error handling for no benefit."""
    mock_get.return_value = _response(401)

    response = request_with_retry("http://example.com", headers={}, max_retries=3)

    assert response.status_code == 401
    assert mock_get.call_count == 1
    mock_sleep.assert_not_called()


@patch("main.time.sleep")
@patch("main.requests.get")
def test_retries_on_server_error_then_succeeds(mock_get, mock_sleep):
    mock_get.side_effect = [_response(503), _response(503), _response(200)]

    response = request_with_retry("http://example.com", headers={}, max_retries=3, backoff_seconds=0.01)

    assert response.status_code == 200
    assert mock_get.call_count == 3
    assert mock_sleep.call_count == 2


@patch("main.time.sleep")
@patch("main.requests.get")
def test_gives_up_after_max_retries_on_persistent_server_error(mock_get, mock_sleep):
    """Returns the last (failing) response rather than raising -- the
    caller (e.g. get_songs) is responsible for calling raise_for_status."""
    mock_get.return_value = _response(503)

    response = request_with_retry("http://example.com", headers={}, max_retries=2, backoff_seconds=0.01)

    assert response.status_code == 503
    assert mock_get.call_count == 3  # initial attempt + 2 retries


@patch("main.time.sleep")
@patch("main.requests.get")
def test_retries_on_connection_error_then_succeeds(mock_get, mock_sleep):
    mock_get.side_effect = [requests.exceptions.ConnectionError(), _response(200)]

    response = request_with_retry("http://example.com", headers={}, max_retries=3, backoff_seconds=0.01)

    assert response.status_code == 200
    assert mock_get.call_count == 2


@patch("main.time.sleep")
@patch("main.requests.get")
def test_raises_after_max_retries_on_persistent_connection_error(mock_get, mock_sleep):
    mock_get.side_effect = requests.exceptions.ConnectionError()

    try:
        request_with_retry("http://example.com", headers={}, max_retries=2, backoff_seconds=0.01)
        assert False, "expected ConnectionError to propagate"
    except requests.exceptions.ConnectionError:
        pass

    assert mock_get.call_count == 3  # initial attempt + 2 retries
