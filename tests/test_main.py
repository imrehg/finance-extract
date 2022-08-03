from pathlib import Path
from unittest import mock

import pytest
from google.api_core.exceptions import NotFound
from google.cloud.bigquery.table import TableReference


def test_read_main(app_client):
    response = app_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_post_email_with_not_supported_address(app_client, generate_test_email):
    """When the server receives an unsupported org,
    we should get back a client error.
    """
    payload = generate_test_email()
    response = app_client.post("/_ah/mail/not-supported@dummy.com", data=payload)

    assert response.status_code == 422
    assert response.json()["detail"] == "Can't handle request type: not-supported"


def test_post_email_to_supported_endpoint_without_attachment(app_client, generate_test_email):
    """When the server receives email a supported org but
    there's no attachment, we should get back a client error."""
    payload = generate_test_email()
    response = app_client.post("/_ah/mail/huanan@dummy.com", data=payload)

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


@mock.patch("app.main.settings.huanan_pass", "Clearly-a-wrong-pass")
def test_post_email_to_supported_endpoint_with_wrong_password(app_client, generate_test_email):
    """When the received encrypted/protected PDF is decrypted
    with the wrong password, we should get back a client error."""
    # Set wrong password
    # mock.patch("app.main.settings.huanan_pass", "Clearly-a-wrong-pass")

    input_file_path = Path(__file__).parent / "assets" / "test00.pdf"
    payload = payload = generate_test_email(input_file_path)
    response = app_client.post("/_ah/mail/huanan@dummy.com", data=payload)

    assert response.status_code == 422
    assert response.json()["detail"] == "PDF encryption passsword as incorrect."


@pytest.mark.skip("Not written")
def test_post_email_to_supported_endpoint_with_correct_pdf_no_table():
    """When the received encrypted PDF doesn't contain any tables,
    we should get back a client error."""
    pass


@mock.patch("app.main.settings.google_cloud_project", "default-project")
@mock.patch("app.main.settings.huanan_pass", "Hello")
def test_post_email_to_supported_endpoint_with_correct_pdf_right_table(
    app_client, generate_test_email, mock_bigquery_client
):
    # Create a new table
    mock_bigquery_client.get_table.side_effect = NotFound("huanan")

    input_file_path = Path(__file__).parent / "assets" / "test00.pdf"
    payload = generate_test_email(input_file_path)
    response = app_client.post("/_ah/mail/huanan@dummy.com", data=payload)

    assert response.status_code == 200
    assert response.text == '"Success"'

    mock_bigquery_client.create_table.assert_called_with(mock.ANY)
    mock_bigquery_client.get_table.assert_called_with(TableReference.from_string("default-project.finance.huanan"))
    table = mock_bigquery_client.create_table.call_args[0][0]
    assert table.project == "default-project"


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
