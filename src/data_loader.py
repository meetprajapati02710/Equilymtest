from __future__ import annotations

from io import StringIO
from typing import Any

import pandas as pd


def load_csv_from_input(uploaded_file: Any) -> pd.DataFrame:
    if uploaded_file is None:
        raise ValueError("No uploaded file was provided.")

    if hasattr(uploaded_file, "getvalue"):
        raw_bytes = uploaded_file.getvalue()
        if isinstance(raw_bytes, bytes):
            text = raw_bytes.decode("utf-8-sig")
        else:
            text = str(raw_bytes)
        return pd.read_csv(StringIO(text))

    return pd.read_csv(uploaded_file)
