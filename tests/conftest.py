import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Optional
from unittest import mock

import google.cloud.bigquery
import google.cloud.secretmanager
import pytest
from fastapi.testclient import TestClient


# Based on https://github.com/googleapis/python-bigquery-pandas/blob/685d1c39f709a58a9bf59fb1cec9474d3e3c03c0/tests/unit/conftest.py
def mock_get_credentials(*args, **kwargs):
    import google.auth.credentials

    mock_credentials = mock.create_autospec(google.auth.credentials.Credentials)
    return mock_credentials, "default-project"


@pytest.fixture
def mock_service_account_credentials():
    import google.oauth2.service_account

    mock_credentials = mock.create_autospec(google.oauth2.service_account.Credentials)
    return mock_credentials


@pytest.fixture(autouse=True)
def no_auth(monkeypatch):
    import pydata_google_auth

    monkeypatch.setattr(pydata_google_auth, "default", mock_get_credentials)


@pytest.fixture(autouse=True)
def mock_bigquery_client(monkeypatch):

    mock_client = mock.create_autospec(google.cloud.bigquery.Client)
    # Constructor returns the mock itself, so this mock can be treated as the
    # constructor or the instance.
    mock_client.return_value = mock_client
    monkeypatch.setattr(google.cloud.bigquery, "Client", mock_client)
    mock_client.reset_mock()

    return mock_client


@pytest.fixture(autouse=True)
def mock_secretmanager_client(monkeypatch):

    mock_client = mock.create_autospec(google.cloud.secretmanager.SecretManagerServiceClient)
    # Constructor returns the mock itself, so this mock can be treated as the
    # constructor or the instance.
    mock_client.return_value = mock_client
    monkeypatch.setattr(google.cloud.secretmanager, "SecretManagerServiceClient", mock_client)
    mock_client.reset_mock()

    return mock_client


@pytest.fixture()
def app_client(mock_secretmanager_client):
    from google.cloud.secretmanager_v1beta1.types import (
        AccessSecretVersionResponse,
        SecretPayload,
    )

    huanan_pass = SecretPayload(data=b"Hello")
    secret_response = AccessSecretVersionResponse(name="projects/*/secrets/*/versions/*", payload=huanan_pass)
    mock_secretmanager_client.access_secret_version.return_value = secret_response

    from app.main import app

    return TestClient(app)


# The functions below handle generating emails to pass to the AppEngine endpoit
def create_attachment_from_file(
    infile_path: Path, mime_maintype: str = "application", mime_subtype: str = "application/pdf"
) -> MIMEBase:
    with open(infile_path, "rb") as fp:
        msg = MIMEBase(mime_maintype, mime_subtype)
        msg.set_payload(fp.read())
    encoders.encode_base64(msg)
    msg.add_header("Content-Disposition", "attachment", filename=infile_path.name)
    return msg


def create_email_as_str(attachment: Optional[MIMEBase] = None) -> str:
    outer = MIMEMultipart()
    outer["Subject"] = "Some test email sent at %s" % datetime.date.today()
    outer["To"] = "recipient@imreh.net"
    outer["From"] = "pytest@imreh.net"
    outer.preamble = "You will not see this in a MIME-aware mail reader.\n"
    outer.attach(MIMEText("A test email."))

    if attachment is not None:
        outer.attach(attachment)

    return outer.as_string()


@pytest.fixture()
def generate_test_email():
    def generate_email_function(
        attachment_infile_path: Optional[Path] = None,
        mime_maintype: str = "application",
        mime_subtype: str = "application/pdf",
    ):
        attachment = (
            create_attachment_from_file(attachment_infile_path, mime_maintype=mime_maintype, mime_subtype=mime_subtype)
            if attachment_infile_path is not None
            else None
        )
        return create_email_as_str(attachment=attachment)

    return generate_email_function


# TODO: create fixtures for test emails generated as GCP-parsed objecs such as:
# https://cloud.google.com/appengine/docs/standard/python3/reference/services/bundled/google/appengine/api/mail/InboundEmailMessage
