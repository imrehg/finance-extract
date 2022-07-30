# -*- coding: utf-8 -*-
import os
import shutil
from io import BytesIO
from pathlib import Path

import pandas as pd
import pikepdf
import tabula  # type: ignore
from fastapi import FastAPI, Request
from google.appengine.api import mail  # type: ignore
from pydantic import BaseSettings, validator

# Hack: install Java which is required for the PDF processing
if shutil.which("java") is None:
    print("Installing Java....")
    import jdk  # type: ignore

    try:
        java_path = Path(jdk.install("11", jre=True)) / "bin"
    except StopIteration:
        jdk.uninstall("11", jre=True)
        java_path = Path(jdk.install("11", jre=True)) / "bin"

    os.environ["PATH"] = str(java_path) + ":" + os.environ["PATH"]
    print(f"Java Path: {java_path}")
    print("Installing Java: Done")
# Hack: End


def access_secret_version(project_id, secret_id, version_id):
    """
    Access the payload for the given secret version if one exists. The version
    can be a version number as a string (e.g. "5") or an alias (e.g. "latest").
    """

    # Import the Secret Manager client library.
    from google.cloud import secretmanager

    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version.
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    # Access the secret version.
    response = client.access_secret_version(request={"name": name})
    payload = response.payload.data.decode("UTF-8")
    return payload


class Settings(BaseSettings):
    google_cloud_project: str
    huanan_pass: str = ""
    bigquery_location: str = "asia-east1"
    bigquery_dataset: str = "finance"
    huanan_table_name: str = "huanan"

    @validator("huanan_pass")
    def load_from_secrets_if_missing(cls, v, values):
        if v == "":
            v = access_secret_version(
                values["google_cloud_project"], "huanan_pass", "latest"
            )
        return v

    class Config:
        env_file = ".env"


settings = Settings()
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/_ah/mail/{address}")
async def receive_mail(address: str, request: Request):
    body = await request.body()
    mail_message = mail.InboundEmailMessage(body)

    # Do something with the message
    print("Received greeting at %s from %s." % (mail_message.to, mail_message.sender))

    organisation = mail_message.to.split("@")[0]
    match organisation:
        case "huanan":
            handle_huanan_data(mail_message)
        case _:
            print(f"Can't handle request type: {organisation}")
    return "Success"


def handle_huanan_data(mail_message) -> None:
    try:
        filename, payload = mail_message.attachments[0]
    except AttributeError:
        for _, encoded_body in mail_message.bodies():
            print(encoded_body.decode())
        print("No attachments in this email.")
        return

    encrypted_pdf = BytesIO(payload.decode())
    pdf = pikepdf.open(encrypted_pdf, password=settings.huanan_pass)
    bio = BytesIO()
    pdf.save(bio)
    dfs = tabula.read_pdf(bio, pages="all")
    transactions = dfs[0]
    cleaned_transactions = huanan_df_cleanup(transactions)

    print(cleaned_transactions)

    cleaned_transactions.to_gbq(
        destination_table=f"{settings.bigquery_dataset}.{settings.huanan_table_name}",
        if_exists="append",
        location=settings.bigquery_location,
    )


def huanan_df_cleanup(df_in):
    df_transactions = df_in.copy()
    column_names_map = {
        0: "CardLastDigits",
        1: "TransactionDate",
        2: "TransactionAmountNTD",
    }
    column_names = [
        column_names_map[col_index] for col_index in sorted(column_names_map.keys())
    ]
    rename_map = {
        df_transactions.columns[col_index]: column_names_map[col_index]
        for col_index in column_names_map
    }

    df_transactions = df_transactions.rename(columns=rename_map)
    df_transactions = df_transactions[column_names]

    df_transactions[["TransactionAmountNTD", "TransactionType"]] = df_transactions[
        "TransactionAmountNTD"
    ].str.split(expand=True)
    df_transactions["TransactionDate"] = pd.to_datetime(
        df_transactions["TransactionDate"], utc=False
    ).dt.tz_localize("Asia/Taipei")
    df_transactions["TransactionAmountNTD"] = df_transactions[
        "TransactionAmountNTD"
    ].apply(lambda value: int(value.replace(",", "")))
    df_transactions["TransactionType"] = df_transactions["TransactionType"].astype(int)
    return df_transactions
