# -*- coding: utf-8 -*-
"""Huanan adapter related tests."""
from pathlib import Path

import pandas as pd
import pytest

from app.adapters import huanan


@pytest.mark.parametrize(
    "input_pdf_name,expected",
    [
        pytest.param(
            "test00.pdf",
            pd.DataFrame(
                {
                    "卡片後四碼": ["2109", "2109"],
                    "消費日": ["2022/07/29 08:54", "2022/07/29 20:33"],
                    "消費金額(新台幣)": ["404", "1,056"],
                    "交易類別": ["1", "1"],
                    "卡片名稱": ["ｉ網購生活卡城市星空", "ｉ網購生活卡城市星空"],
                    "正卡/附卡": ["正卡", "正卡"],
                }
            ),
        ),
        pytest.param(
            "test01.pdf",
            pd.DataFrame(
                {
                    "卡片後四碼": ["2109"],
                    "消費日": ["2022/07/25 12:16"],
                    "消費金額(新台幣)": ["60"],
                    "交易類別": ["1"],
                    "卡片名稱": ["ｉ網購生活卡城市星空"],
                    "正卡/附卡": ["正卡"],
                }
            ),
        ),
    ],
)
def test_huanan_table_extraction(input_pdf_name, expected):
    """When a PDF is passed in, the correct dataframe content is extracted."""
    assets_path = Path(__file__).parent / "assets"
    test_pdf_path = assets_path / input_pdf_name
    df_extracted = huanan.huanan_extract_table_from_pdf(test_pdf_path, pdf_pass="Hello")

    assert df_extracted.equals(expected)


def test_huanan_df_cleanup():
    """When a dataframe is passed in, it is cleaned up correctly
    according to the Huanan format."""

    data_in = {
        "卡片後四碼": ["1234", "5678"],
        "消費日": ["2022/07/29 12:33", "2022/07/29 15:54"],
        "消費金額(新台幣)": ["1,456", "345"],
        "交易類別": ["1", "2"],
        "卡片名稱": ["ｉ網購生活卡城市星空", "ｉ網購生活卡城市星空"],
        "正卡/附卡": ["正卡", "附卡"],
    }
    df_in = pd.DataFrame(data_in)

    data_expected = {
        "CardLastDigits": ["1234", "5678"],
        "TransactionDate": pd.to_datetime(["2022-07-29 12:33:00+08:00", "2022-07-29 15:54:00+08:00"]),
        "TransactionAmountNTD": [1456, 345],
        "TransactionType": [1, 2],
    }
    df_expected = pd.DataFrame(data_expected)
    # Do the named timezone.
    df_expected["TransactionDate"] = df_expected["TransactionDate"].dt.tz_convert("Asia/Taipei")

    # Do the actual conversion test
    df_cleaned = huanan.huanan_df_cleanup(df_in)

    assert df_cleaned.equals(df_expected)
