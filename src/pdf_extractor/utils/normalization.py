from __future__ import annotations

from typing import Any, Iterable


def dataframe_to_rows(df: Any) -> list[list[str]]:
    """Converte um DataFrame pandas em lista de strings sem depender do tipo em tempo de importação."""

    if df is None:
        return []

    try:
        import pandas as pd  # type: ignore
    except Exception:  # pragma: no cover
        return []

    if not isinstance(df, pd.DataFrame):
        return []

    cleaned = df.fillna("").astype(str)
    return cleaned.values.tolist()


def ensure_text(chunks: Iterable[str]) -> str:
    return "\n".join(part for part in chunks if part).strip()

