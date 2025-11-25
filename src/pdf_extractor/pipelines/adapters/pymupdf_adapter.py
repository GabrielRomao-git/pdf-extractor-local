from __future__ import annotations

from pathlib import Path

from pdf_extractor.pipelines.base import (
    AdapterRuntimeError,
    ExtractionBundle,
    FigureArtifact,
    TableArtifact,
    ToolAdapter,
)


class PyMuPDFAdapter(ToolAdapter):
    name = "pymupdf"
    display_name = "PyMuPDF"
    description = "Extração com fitz (PyMuPDF) em modo texto + tabelas heurísticas"

    def extract(self, pdf_path: Path) -> ExtractionBundle:
        """Processa o PDF com fitz, reunindo texto, tabelas heurísticas e figuras."""
        try:
            import fitz
        except Exception as exc:  # pragma: no cover - import heavy
            raise AdapterRuntimeError("PyMuPDF (fitz) não está disponível.") from exc

        try:
            document = fitz.open(pdf_path)
        except Exception as exc:
            raise AdapterRuntimeError(f"PyMuPDF não conseguiu abrir {pdf_path.name}: {exc}") from exc

        texts: list[str] = []
        tables: list[TableArtifact] = []
        figures: list[FigureArtifact] = []

        for page_number, page in enumerate(document, start=1):
            texts.append(page.get_text("text").strip())
            tables.extend(self._extract_tables(page, page_number))
            figures.extend(self._extract_figures(page, page_number))

        metadata = {"engine": "pymupdf", "num_pages": document.page_count}
        document.close()
        return ExtractionBundle(text="\n\n".join(texts), tables=tables, figures=figures, metadata=metadata)

    def _extract_tables(self, page, page_number: int) -> list[TableArtifact]:
        """Tenta identificar tabelas via `find_tables` e normaliza linhas por página."""
        tables: list[TableArtifact] = []
        try:
            finder = page.find_tables()
        except Exception:
            return tables

        for idx, table in enumerate(getattr(finder, "tables", []) or []):
            try:
                raw_rows = table.extract()
            except Exception:
                raw_rows = []
            clean_rows = []
            for row in raw_rows:
                if isinstance(row, (list, tuple)):
                    clean_rows.append([str(cell or "").strip() for cell in row])
            tables.append(
                TableArtifact(
                    rows=clean_rows,
                    page=page_number,
                    metadata={"source": "pymupdf", "idx": idx},
                )
            )
        return tables

    def _extract_figures(self, page, page_number: int) -> list[FigureArtifact]:
        """Mapeia imagens da página para artefatos de figura com metadados básicos."""
        figures: list[FigureArtifact] = []
        try:
            images = page.get_images(full=True)
        except Exception:
            images = []
        for img in images:
            xref = img[0]
            width, height = img[2], img[3]
            figures.append(
                FigureArtifact(
                    caption=None,
                    page=page_number,
                    description=f"Imagem xref {xref}",
                    metadata={"width": width, "height": height},
                )
            )
        return figures

