import pytest
import requests

from codex_of_the_damned import app


def pytest_sessionstart(session):
    # Do not launch tests is there is no proper Internet connection.
    try:
        requests.get("http://www.google.com", timeout=1)
    except requests.exceptions.RequestException:
        pytest.fail("No internet connection")
    try:
        requests.get("https://api.krcg.org", timeout=1)
    except requests.exceptions.RequestException:
        pytest.fail("KRCG API not available")


@pytest.fixture(scope="session")
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client
