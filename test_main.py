import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


@pytest.mark.skip("Not written")
def test_post_email_with_not_supported_address():
    pass


@pytest.mark.skip("Not written")
def test_post_email_to_supported_endpoint_without_attachment():
    pass


@pytest.mark.skip("Not written")
def test_post_email_to_supported_endpoint_with_not_pdf():
    pass


@pytest.mark.skip("Not written")
def test_post_email_to_supported_endpoint_with_not_encrypted_pdf():
    pass


@pytest.mark.skip("Not written")
def test_post_email_to_supported_endpoint_with_wrong_password():
    pass


@pytest.mark.skip("Not written")
def test_post_email_to_supported_endpoint_with_correct_pdf_no_table():
    pass


@pytest.mark.skip("Not written")
def test_post_email_to_supported_endpoint_with_correct_pdf_right_table():
    pass


@pytest.mark.skip("Not written")
def test_pdf_to_table_conversion():
    pass


@pytest.mark.skip("Not written")
def test_data_table_to_bigquery():
    pass
