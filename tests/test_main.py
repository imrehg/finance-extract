import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Optional

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture
def mock_service_account_credentials(mocker):
    import google.oauth2.service_account

    mock_credentials = mocker.create_autospec(google.oauth2.service_account.Credentials)
    return mock_credentials


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


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_post_email_with_not_supported_address():
    """When the server receives an unsupported org,
    we should get back a client error.
    """
    payload = create_email_as_str()
    response = client.post("/_ah/mail/not-supported@dummy.com", data=payload)

    assert response.status_code == 422
    assert response.json()["detail"] == "Can't handle request type: not-supported"


def test_post_email_to_supported_endpoint_without_attachment():
    """When the server receives email a supported org but
    there's no attachment, we should get back a client error."""
    payload = create_email_as_str()
    response = client.post("/_ah/mail/huanan@dummy.com", data=payload)

    assert response.status_code == 422
    assert response.json()["detail"] == "No attachments in this email."


@pytest.mark.skip("Not written")
def test_post_email_to_supported_endpoint_with_not_pdf():
    """When the server receives and email but attachment is not a PDF,
    we should get back a client error."""
    pass


@pytest.mark.skip("Not written")
def test_post_email_to_supported_endpoint_with_not_encrypted_pdf():
    """When the received PDF is not encrypted, things should just succeed."""
    pass


def test_post_email_to_supported_endpoint_with_wrong_password(mocker):
    """When the received encrypted/protected PDF is decripted
    with the wrong password, we should get back a client error."""
    # Set wrong password
    mocker.patch("app.main.settings.huanan_pass", "Clearly-a-wrong-pass")

    input_file_path = Path(__file__).parent / "assets" / "test00.pdf"
    attachment = create_attachment_from_file(input_file_path)
    payload = create_email_as_str(attachment)
    response = client.post("/_ah/mail/huanan@dummy.com", data=payload)

    assert response.status_code == 422
    assert response.json()["detail"] == "PDF encryption passsword as incorrect."


@pytest.mark.skip("Not written")
def test_post_email_to_supported_endpoint_with_correct_pdf_no_table():
    """When the received encrypted PDF doesn't contain any tables,
    we should get back a client error."""
    pass


def test_post_email_to_supported_endpoint_with_correct_pdf_right_table(mocker, mock_bigquery_client):
    from google.api_core.exceptions import NotFound
    from google.cloud.bigquery.table import TableReference

    mock_bigquery_client.get_table.side_effect = NotFound("huanan")

    mocker.patch("app.main.settings.google_cloud_project", "pytest-project")
    mocker.patch("app.main.settings.huanan_pass", "Hello")

    input_file_path = Path(__file__).parent / "assets" / "test00.pdf"
    attachment = create_attachment_from_file(input_file_path)
    payload = create_email_as_str(attachment)
    response = client.post("/_ah/mail/huanan@dummy.com", data=payload)

    assert response.status_code == 200
    assert response.text == '"Success"'

    mock_bigquery_client.create_table.assert_called_with(mocker.ANY)
    mock_bigquery_client.get_table.assert_called_with(TableReference.from_string("pytest-project.finance_dev.huanan"))
    table = mock_bigquery_client.create_table.call_args[0][0]
    assert table.project == "pytest-project"


@pytest.mark.skip("Not written")
def test_pdf_to_table_conversion():
    """PDF to table conversion working as expected."""
    pass


@pytest.mark.skip("Not written")
def test_data_table_to_bigquery():
    """Pushing data to BigQuery correctly."""
    pass


@pytest.mark.skip("Not written")
def test_multiple_tables_in_different_order():
    """When multiple tables are extracted, the right
    order is observed."""
    pass


@pytest.mark.skip("Not written")
def test_table_qa_fail():
    pass
