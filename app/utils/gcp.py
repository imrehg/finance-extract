"""Utilities collections
"""

# Import the Secret Manager client library.
from google.cloud import secretmanager

# Adapted from the GCP docs/samples
# https://github.com/googleapis/python-secret-manager/blob/83a03f6f82d82124591119095217cdff61556bee/samples/snippets/access_secret_version.py


def access_secret_version(project_id, secret_id, version_id):
    """
    Access the payload for the given secret version if one exists. The version
    can be a version number as a string (e.g. "5") or an alias (e.g. "latest").
    """
    # Build the resource name of the secret version.
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    # Create the Secret Manager client.
    secret_manager_client = secretmanager.SecretManagerServiceClient()

    # Access the secret version.
    response = secret_manager_client.access_secret_version(request={"name": name})
    payload = response.payload.data.decode("UTF-8")
    return payload
