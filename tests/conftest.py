import google.cloud.bigquery
import pytest


# Based on https://github.com/googleapis/python-bigquery-pandas/blob/685d1c39f709a58a9bf59fb1cec9474d3e3c03c0/tests/unit/conftest.py
@pytest.fixture(autouse=True)
def mock_bigquery_client(monkeypatch, mocker):

    mock_client = mocker.create_autospec(google.cloud.bigquery.Client)
    # Constructor returns the mock itself, so this mock can be treated as the
    # constructor or the instance.
    mock_client.return_value = mock_client
    monkeypatch.setattr(google.cloud.bigquery, "Client", mock_client)
    mock_client.reset_mock()

    return mock_client
