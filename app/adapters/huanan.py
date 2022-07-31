"""Huanan finance data handling
"""
import logging
from io import BytesIO

import pandas as pd
import pdfplumber

logger = logging.getLogger("uvicorn.error")


def handle_data(
    mail_message, pdf_pass: str, bigquery_dataset: str, huanan_table_name: str, bigquery_location: str
) -> None:
    try:
        # Get the first attachment
        filename, payload = mail_message.attachments[0]
    except AttributeError:
        # If no attachment, print the email text
        # This is important if e.g. automatic forwarding is set up
        # as the confirmation code is in the email body.
        for _, encoded_body in mail_message.bodies():
            logger.info(encoded_body.decode())
        raise AttributeError("No attachments in this email.")
    if not filename.lower().endswith(".pdf"):
        raise AttributeError(f"Wrong attachment type, filename: {filename}")

    encrypted_pdf = BytesIO(payload.decode())
    transactions = huanan_extract_table_from_pdf(encrypted_pdf, pdf_pass)
    cleaned_transactions = huanan_df_cleanup(transactions)
    print(cleaned_transactions)

    x = cleaned_transactions.to_gbq(
        destination_table=f"{bigquery_dataset}.{huanan_table_name}",
        if_exists="append",
        location=bigquery_location,
    )
    print(x)
    logger.info("BigQuery upload finished.")


def huanan_extract_table_from_pdf(input_pdf, pdf_pass: str):
    pdf = pdfplumber.open(input_pdf, password=pdf_pass)
    page0 = pdf.pages[0]
    table = page0.extract_table()

    # Small QA
    if len(table) < 2:
        raise ValueError(f"Extracted table is not the expected size: {table}")

    if table[0][0] != "卡片後四碼":
        raise AttributeError(f"Haven't found correct table header: {table[0]}")

    return pd.DataFrame(table[1:], columns=table[0])


def huanan_df_cleanup(df_in):
    df_transactions = df_in.copy()
    column_names_map = {
        0: "CardLastDigits",
        1: "TransactionDate",
        2: "TransactionAmountNTD",
        3: "TransactionType",
    }
    column_names = [column_names_map[col_index] for col_index in sorted(column_names_map.keys())]
    rename_map = {df_transactions.columns[col_index]: column_names_map[col_index] for col_index in column_names_map}

    df_transactions = df_transactions.rename(columns=rename_map)
    df_transactions = df_transactions[column_names]

    df_transactions["TransactionDate"] = pd.to_datetime(df_transactions["TransactionDate"], utc=False).dt.tz_localize(
        "Asia/Taipei"
    )

    df_transactions["TransactionAmountNTD"] = df_transactions["TransactionAmountNTD"].apply(
        lambda value: int(value.replace(",", ""))
    )

    df_transactions["TransactionType"] = df_transactions["TransactionType"].astype(int)

    return df_transactions
