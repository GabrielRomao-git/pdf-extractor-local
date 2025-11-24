from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from pdf_extractor.pipelines.base import (
    AdapterRuntimeError,
    ExtractionBundle,
    FigureArtifact,
    TableArtifact,
    ToolAdapter,
)
from pdf_extractor.utils import dataframe_to_rows


def _coerce_value(value: Any) -> Any:
    if callable(value):
        try:
            return value()
        except Exception:
            return None
    return value


def _ensure_str(value: Any) -> str:
    coerced = _coerce_value(value)
    if coerced is None:
        return ""
    if isinstance(coerced, str):
        return coerced.strip()
    return str(coerced)


def _coerce_number(value: Any) -> int | float | None:
    coerced = _coerce_value(value)
    if isinstance(coerced, (int, float)):
        return coerced
    try:
        return float(coerced) if coerced is not None else None
    except (TypeError, ValueError):
        return None


class DoclingAdapter(ToolAdapter):
    name = "docling"
    display_name = "Docling"
    description = "Conversor Docling para Markdown estruturado"

    def __init__(self) -> None:
        try:
            from docling.document_converter import DocumentConverter
        except Exception as exc:  # pragma: no cover - import heavy
            raise AdapterRuntimeError("Docling não está instalado ou falhou ao inicializar.") from exc

        self._converter = DocumentConverter()

    def extract(self, pdf_path: Path) -> ExtractionBundle:
        try:
            result = self._converter.convert(pdf_path)
        except Exception as exc:
            raise AdapterRuntimeError(f"Docling falhou ao processar {pdf_path.name}: {exc}") from exc

        document = getattr(result, "document", None)
        text = self._export_markdown(result, document)
        tables = self._parse_tables(result, document)
        figures = self._parse_figures(result, document)

        metadata = {
            "engine": "docling",
            "num_pages": _coerce_number(getattr(document, "num_pages", None)),
            "version": _ensure_str(getattr(result, "version", None)) or None,
        }
        return ExtractionBundle(text=text, tables=tables, figures=figures, metadata=metadata)

    def _export_markdown(self, result: Any, document: Any) -> str:
        exporter = getattr(document, "export_to_markdown", None)
        if callable(exporter):
            try:
                return _ensure_str(exporter())
            except Exception:
                pass
        fallback = (
            _coerce_value(getattr(result, "markdown", None))
            or _coerce_value(getattr(result, "text", None))
            or _coerce_value(getattr(result, "text_markdown", None))
            or ""
        )
        return _ensure_str(fallback)

    def _parse_tables(self, result: Any, document: Any) -> list[TableArtifact]:
        tables: list[TableArtifact] = []
        table_sources = getattr(document, "tables", None) or getattr(result, "tables", None) or []
        for idx, table in enumerate(table_sources):
            rows = self._extract_rows(table)
            caption = _ensure_str(getattr(table, "caption", None) or getattr(table, "title", None)) or None
            tables.append(
                TableArtifact(
                    rows=rows,
                    caption=caption,
                    page=_coerce_number(getattr(table, "page", None)),
                    metadata={"idx": idx},
                )
            )
        return tables

    def _parse_figures(self, result: Any, document: Any) -> list[FigureArtifact]:
        figure_sources = getattr(document, "figures", None) or getattr(result, "figures", None) or []
        figures: list[FigureArtifact] = []
        for idx, figure in enumerate(figure_sources):
            caption = _ensure_str(getattr(figure, "caption", None) or getattr(figure, "title", None)) or None
            description = _ensure_str(getattr(figure, "description", None)) or None
            figures.append(
                FigureArtifact(
                    caption=caption,
                    page=_coerce_number(getattr(figure, "page", None)),
                    description=description,
                    metadata={"idx": idx},
                )
            )
        return figures

    def _extract_rows(self, table: Any) -> list[list[str]]:
        strategies: list[Callable[[], list[list[str]]]] = []
        if hasattr(table, "df"):
            strategies.append(lambda tbl=table: dataframe_to_rows(tbl.df))
        if hasattr(table, "to_pandas"):
            strategies.append(lambda tbl=table: dataframe_to_rows(tbl.to_pandas()))
        if hasattr(table, "cells"):
            strategies.append(lambda tbl=table: [self._clean_row(row) for row in getattr(tbl, "cells", [])])
        if hasattr(table, "export_markdown"):
            strategies.append(lambda tbl=table: self._markdown_to_rows(_ensure_str(tbl.export_markdown())))

        for producer in strategies:
            try:
                rows = producer()
            except Exception:
                continue
            if rows:
                return rows
        return []

    def _markdown_to_rows(self, markdown: str) -> list[list[str]]:
        rows: list[list[str]] = []
        for line in markdown.splitlines():
            line = line.strip()
            if not line.startswith("|") or set(line) <= {"|", "-", ":"}:
                continue
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            rows.append(cells)
        return rows

    def _clean_row(self, row: Any) -> list[str]:
        cleaned: list[str] = []
        data = row
        if callable(row):
            try:
                data = row()
            except Exception:
                data = []
        for cell in data or []:
            text = getattr(cell, "text", None)
            if text is None and hasattr(cell, "content"):
                text = getattr(cell, "content")
            cleaned.append(_ensure_str(text))
        return cleaned

