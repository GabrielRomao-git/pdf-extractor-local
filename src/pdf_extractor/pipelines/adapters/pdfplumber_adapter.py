from __future__ import annotations

from pathlib import Path

from pdf_extractor.pipelines.base import (
    AdapterRuntimeError,
    ExtractionBundle,
    TableArtifact,
    ToolAdapter,
)


class PdfPlumberAdapter(ToolAdapter):
    name = "pdfplumber"
    display_name = "pdfplumber"
    description = "Extração de texto e tabelas com pdfplumber"

    def extract(self, pdf_path: Path) -> ExtractionBundle:
        """Abre o PDF com pdfplumber e retorna texto contínuo e tabelas básicas."""
        try:
            import pdfplumber
        except Exception as exc:  # pragma: no cover - import heavy
            raise AdapterRuntimeError("pdfplumber não está instalado.") from exc

        try:
            doc = pdfplumber.open(pdf_path)
        except Exception as exc:
            raise AdapterRuntimeError(f"pdfplumber não conseguiu abrir {pdf_path.name}: {exc}") from exc

        texts: list[str] = []
        tables: list[TableArtifact] = []

        with doc:
            for page_number, page in enumerate(doc.pages, start=1):
                texts.append((page.extract_text() or "").strip())
                try:
                    raw_tables = page.extract_tables()
                except Exception:
                    raw_tables = []
                for idx, raw in enumerate(raw_tables):
                    cleaned = [[(cell or "").strip() for cell in row] for row in raw]
                    tables.append(
                        TableArtifact(
                            rows=cleaned,
                            page=page_number,
                            metadata={"source": "pdfplumber", "idx": idx},
                        )
                    )

        metadata = {"engine": "pdfplumber", "num_pages": len(doc.pages)}
        return ExtractionBundle(text="\n\n".join(texts), tables=tables, figures=[], metadata=metadata)

