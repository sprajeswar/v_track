"""Place for all tests with mock when required."""

# tests/services/test_vulners_call_api.py
import logging
import pytest
from http import HTTPStatus

logger = logging.getLogger("tests.call_api")


@pytest.mark.positive
def test_call_api_positive(monkeypatch, pipeline_e2e_fixture):
    """Positive scenario: 
        To simulate successful API call returning HTTP 200.
    """
    service, _ = pipeline_e2e_fixture

    class MockResponse:
        status_code = HTTPStatus.OK
        def json(self):
            return {"results": [{"status": "ok"}]}

    # Mock requests.post to always return MockResponse
    def fake_post(url, data, headers):
        logger.info("Mock POST called with URL=%s", url)
        return MockResponse()

    import requests
    monkeypatch.setattr(requests, "post", fake_post)

    # Call the method under test
    payload = '{"package": "Flask"}'
    response = service.call_api("https://api.osv.dev/", payload)

    # Positive assertions
    assert response.status_code == HTTPStatus.OK
    assert response.json()["results"][0]["status"] == "ok"

    logger.info("Positive test passed: call_api returned 200 successfully.")


@pytest.mark.negative
def test_call_api_negative(monkeypatch, pipeline_e2e_fixture):
    """Negative scenario:
        To simulate failed API call (500 Internal Server Error)."""
    service, _ = pipeline_e2e_fixture

    class MockResponse:
        status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        def json(self):
            return {"error": "server failure"}

    def fake_post(url, data, headers):
        logger.warning("Mock POST failed with URL=%s", url)
        return MockResponse()

    import requests
    monkeypatch.setattr(requests, "post", fake_post)

    # Invoke method under test
    payload = '{"package": "Django"}'
    response = service.call_api("https://api.osv.dev/", payload)

    # This is still positive assertions
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert "error" in response.json()

    logger.info("Negative test passed: call_api handled 500 response correctly.")
