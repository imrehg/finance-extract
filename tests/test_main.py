import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


@pytest.mark.skip("Not written")
def test_post_email_with_not_supported_address():
    """When the server receives an unsupported org,
    we should get back a client error.
    """
    pass


@pytest.mark.skip("Not written")
def test_post_email_to_supported_endpoint_without_attachment():
    """When the server receives email a supported org but
    there's no attachment, we should get back a client error."""
    pass


@pytest.mark.skip("Not written")
def test_post_email_to_supported_endpoint_with_not_pdf():
    """When the server receives and email but attachment is not a PDF,
    we should get back a client error."""
    pass


@pytest.mark.skip("Not written")
def test_post_email_to_supported_endpoint_with_not_encrypted_pdf():
    """When the received PDF is not encrypted, we should get
    back a client error."""
    pass


@pytest.mark.skip("Not written")
def test_post_email_to_supported_endpoint_with_wrong_password():
    """When the received encrypted/protected PDF is decripted
    with the wrong password, we should get back a client error."""
    pass


@pytest.mark.skip("Not written")
def test_post_email_to_supported_endpoint_with_correct_pdf_no_table():
    """When the received encrypted PDF doesn't contain any tables,
    we should get back a client error."""
    pass


@pytest.mark.skip("Not written")
def test_post_email_to_supported_endpoint_with_correct_pdf_right_table():
    pass


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
