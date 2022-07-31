# -*- coding: utf-8 -*-
"""Huanan adapter related tests."""
import pandas as pd

from app.adapters import huanan


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
