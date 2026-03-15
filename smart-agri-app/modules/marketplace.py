from __future__ import annotations

import pandas as pd

from .storage import get_buyer_marketplace


def list_buyers(crop: str | None = None) -> pd.DataFrame:
    return get_buyer_marketplace(crop)
