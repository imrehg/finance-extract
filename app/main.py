# -*- coding: utf-8 -*-
import logging

from fastapi import FastAPI, HTTPException, Request
from google.appengine.api import mail  # type: ignore
from google.auth.exceptions import DefaultCredentialsError
from pydantic import BaseSettings, validator

from .adapters import huanan
from .utils import gcp

# If this server is run with bare uvicorn, log lines will be duplicated
# When run with gunicorn + UvicornWorker, it will be single line in main log
logger = logging.getLogger("uvicorn.error")


class Settings(BaseSettings):
    google_cloud_project: str
    huanan_pass: str = ""
    bigquery_location: str = "asia-east1"
    bigquery_dataset: str = "finance"
    huanan_table_name: str = "huanan"

    @validator("huanan_pass")
    def load_from_secrets_if_missing(cls, v, values):
        if v == "":
            try:
                v = gcp.access_secret_version(values["google_cloud_project"], "huanan_pass", "latest")
            except DefaultCredentialsError:
                logger.warning("huanan_pass setting is empty")
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
    logging.info("Arrived!")
    body = await request.body()
    mail_message = mail.InboundEmailMessage(body)

    logger.info(
        f'Received request, email to "{mail_message.to}" '
        + f'from "{mail_message.sender}" '
        + f'with subject "{mail_message.subject}"'
    )

    # We are splitting functionality by the server receive address ie. endpoint
    organisation = address.split("@")[0]
    match organisation:
        case "huanan":
            try:
                huanan.handle_data(
                    mail_message,
                    pdf_pass=settings.huanan_pass,
                    bigquery_dataset=settings.bigquery_dataset,
                    huanan_table_name=settings.huanan_table_name,
                    bigquery_location=settings.bigquery_location,
                )
            except BaseException as e:
                raise HTTPException(status_code=422, detail=str(e))
        case _:
            print(f"Can't handle request type: {organisation}")
    return "Success"
