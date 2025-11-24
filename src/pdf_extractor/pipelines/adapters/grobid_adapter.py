from __future__ import annotations

import os
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

from pdf_extractor.pipelines.base import (
    AdapterRuntimeError,
    ExtractionBundle,
    FigureArtifact,
    TableArtifact,
    ToolAdapter,
)


class GrobidAdapter(ToolAdapter):
    name = "grobid"
    display_name = "Grobid"
    description = "Serviço Grobid (TEI) - requer container ativo"

    def __init__(self, base_url: str | None = None, timeout: float = 120.0) -> None:
        self.base_url = base_url or os.getenv("GROBID_URL", "http://grobid:8070")
        self.endpoint = f"{self.base_url.rstrip('/')}/api/processFulltextDocument"
        self.timeout = timeout

    def extract(self, pdf_path: Path) -> ExtractionBundle:
        try:
            with pdf_path.open("rb") as handle:
                files = {"input": (pdf_path.name, handle, "application/pdf")}
                response = httpx.post(self.endpoint, files=files, timeout=self.timeout)
        except Exception as exc:
            raise AdapterRuntimeError(f"Falha ao chamar Grobid: {exc}") from exc

        if response.status_code >= 300:
            raise AdapterRuntimeError(
                f"Grobid retornou {response.status_code}: {response.text[:200]}"
            )

        soup = BeautifulSoup(response.text, "lxml-xml")
        text = self._extract_text(soup)
        tables = self._extract_tables(soup)
        figures = self._extract_figures(soup)
        metadata = {"engine": "grobid", "endpoint": self.endpoint}
        return ExtractionBundle(text=text, tables=tables, figures=figures, metadata=metadata)

    def _extract_text(self, soup: BeautifulSoup) -> str:
        paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
        return "\n\n".join(paragraphs)

    def _extract_tables(self, soup: BeautifulSoup) -> list[TableArtifact]:
        tables: list[TableArtifact] = []
        for idx, table in enumerate(soup.find_all("table")):
            rows = []
            for row in table.find_all("row"):
                cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["cell", "head"])]
                if cells:
                    rows.append(cells)
            caption = None
            figure_parent = table.find_parent("figure")
            if figure_parent:
                desc = figure_parent.find("head") or figure_parent.find("figDesc")
                if desc:
                    caption = desc.get_text(" ", strip=True)
            tables.append(
                TableArtifact(
                    rows=rows,
                    caption=caption,
                    metadata={"source": "grobid", "idx": idx},
                )
            )
        return tables

    def _extract_figures(self, soup: BeautifulSoup) -> list[FigureArtifact]:
        figures: list[FigureArtifact] = []
        for idx, figure in enumerate(soup.find_all("figure")):
            if figure.find("table"):
                continue
            caption_tag = figure.find("head") or figure.find("figDesc")
            caption = caption_tag.get_text(" ", strip=True) if caption_tag else None
            figures.append(
                FigureArtifact(
                    caption=caption,
                    description=figure.get("type"),
                    metadata={"source": "grobid", "idx": idx},
                )
            )
        return figures

