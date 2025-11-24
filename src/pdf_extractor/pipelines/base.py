from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class TableArtifact:
    rows: list[list[str]]
    caption: str | None = None
    page: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "rows": self.rows,
            "caption": self.caption,
            "page": self.page,
            "metadata": self.metadata,
        }


@dataclass(slots=True)
class FigureArtifact:
    caption: str | None = None
    page: int | None = None
    description: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "caption": self.caption,
            "page": self.page,
            "description": self.description,
            "metadata": self.metadata,
        }


@dataclass(slots=True)
class ExtractionBundle:
    text: str
    tables: list[TableArtifact] = field(default_factory=list)
    figures: list[FigureArtifact] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "tables": [table.to_dict() for table in self.tables],
            "figures": [figure.to_dict() for figure in self.figures],
            "metadata": self.metadata,
        }


@dataclass(slots=True)
class ExtractionMetrics:
    pdf_name: str
    tool_name: str
    elapsed_seconds: float
    text_characters: int
    tables_count: int
    figures_count: int
    table_quality: float
    notes: str = ""
    success: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "pdf_name": self.pdf_name,
            "tool": self.tool_name,
            "elapsed_seconds": round(self.elapsed_seconds, 3),
            "text_characters": self.text_characters,
            "tables_count": self.tables_count,
            "figures_count": self.figures_count,
            "table_quality": self.table_quality,
            "notes": self.notes,
            "success": self.success,
        }


@dataclass(slots=True)
class ExtractionResult:
    pdf_path: Path
    tool_name: str
    bundle: ExtractionBundle
    metrics: ExtractionMetrics
    artifact_dir: Path
    error: str | None = None

    def to_summary(self) -> dict[str, Any]:
        payload = {
            **self.metrics.to_dict(),
            "artifact_dir": str(self.artifact_dir),
            "metadata": self.bundle.metadata,
        }
        if self.error:
            payload["error"] = self.error
        return payload

    def to_markdown(self) -> str:
        header = f"# {self.pdf_path.name} · {self.tool_name}\n\n"
        info = (
            f"- Tempo: {self.metrics.elapsed_seconds:.2f}s\n"
            f"- Caracteres: {self.metrics.text_characters}\n"
            f"- Tabelas: {self.metrics.tables_count} "
            f"(qualidade ~{self.metrics.table_quality:.0%})\n"
            f"- Figuras: {self.metrics.figures_count}\n"
        )
        body = self.bundle.text.strip() or "_Sem texto extraído_"
        return f"{header}{info}\n---\n\n{body}\n"


class AdapterRuntimeError(RuntimeError):
    """Erro lançado quando uma ferramenta falha durante a extração."""


class ToolAdapter:
    name: str = "base"
    display_name: str = "Base Adapter"
    description: str = ""

    def extract(self, pdf_path: Path) -> ExtractionBundle:
        raise NotImplementedError

    def metadata(self) -> dict[str, Any]:
        return {"name": self.name, "display_name": self.display_name}


def estimate_table_quality(tables: list[TableArtifact]) -> float:
    if not tables:
        return 0.0
    rich_tables = sum(
        1 for table in tables if len(table.rows) >= 2 and any(cell for row in table.rows for cell in row)
    )
    return round(rich_tables / len(tables), 2)

