from __future__ import annotations

import re
from pathlib import Path

from pdf_extractor.pipelines.base import (
    AdapterRuntimeError,
    ExtractionBundle,
    TableArtifact,
    ToolAdapter,
)


def extract_tables_from_markdown(markdown: str) -> list[TableArtifact]:
    tables: list[TableArtifact] = []
    current: list[str] = []
    for line in markdown.splitlines():
        if re.match(r"^\s*\|.*\|\s*$", line):
            current.append(line.strip())
        else:
            if current:
                tables.append(_markdown_table_to_artifact(current))
                current = []
    if current:
        tables.append(_markdown_table_to_artifact(current))
    return tables


def _markdown_table_to_artifact(rows: list[str]) -> TableArtifact:
    clean_rows: list[list[str]] = []
    for row in rows:
        row = row.strip()
        if set(row) <= {"|", "-", ":", " "}:
            continue
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        clean_rows.append(cells)
    return TableArtifact(rows=clean_rows, metadata={"source": "markdown"})


class MarkitdownAdapter(ToolAdapter):
    name = "markitdown"
    display_name = "MarkItDown"
    description = "Conversão via MarkItDown com realce em Markdown"

    def __init__(self) -> None:
        try:
            from markitdown import MarkItDown
        except Exception as exc:  # pragma: no cover - import heavy
            raise AdapterRuntimeError("MarkItDown não está instalado.") from exc

        self._converter = MarkItDown()

    def extract(self, pdf_path: Path) -> ExtractionBundle:
        try:
            result = self._converter.convert(str(pdf_path))
        except Exception as exc:
            raise AdapterRuntimeError(f"MarkItDown falhou para {pdf_path.name}: {exc}") from exc

        markdown = getattr(result, "text_content", None) or str(result)
        tables = extract_tables_from_markdown(markdown)
        metadata = {"engine": "markitdown"}
        return ExtractionBundle(text=markdown, tables=tables, figures=[], metadata=metadata)

