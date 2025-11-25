from __future__ import annotations

import json
import shutil
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from pdf_extractor.pipelines.adapters import ADAPTER_TYPES
from pdf_extractor.pipelines.base import (
    AdapterRuntimeError,
    ExtractionBundle,
    ExtractionMetrics,
    ExtractionResult,
    FigureArtifact,
    TableArtifact,
    ToolAdapter,
    estimate_table_quality,
)


@dataclass(slots=True)
class ExtractionOptions:
    tool_names: tuple[str, ...]

    @classmethod
    def defaults(cls) -> "ExtractionOptions":
        """Retorna opções contendo todas as ferramentas registradas."""
        return cls(tool_names=tuple(ADAPTER_TYPES.keys()))

    @classmethod
    def from_tool_list(cls, tools: str | None) -> "ExtractionOptions":
        """Cria opções a partir de uma lista separada por vírgula."""
        if not tools:
            return cls.defaults()
        names = tuple(tool.strip() for tool in tools.split(",") if tool.strip())
        return cls(tool_names=names)

    def validate(self) -> None:
        """Garante que todos os nomes de ferramentas são suportados."""
        invalid = [name for name in self.tool_names if name not in ADAPTER_TYPES]
        if invalid:
            raise ValueError(f"Ferramentas inválidas: {', '.join(invalid)}")


class ExtractionManager:
    def __init__(self, artifact_dir: Path, overwrite: bool = False) -> None:
        """Configura diretório de artefatos e cache interno de adaptadores."""
        self.artifact_dir = Path(artifact_dir)
        self.overwrite = overwrite
        self._adapter_cache: dict[str, ToolAdapter] = {}
        self.artifact_dir.mkdir(parents=True, exist_ok=True)

    def run_batch(
        self,
        pdf_paths: Iterable[Path],
        options: ExtractionOptions | None = None,
    ) -> list[list[ExtractionResult]]:
        """Executa todas as ferramentas selecionadas sobre uma lista de PDFs."""
        options = options or ExtractionOptions.defaults()
        options.validate()
        results: list[list[ExtractionResult]] = []
        comparativo: list[dict[str, object]] = []

        for pdf_path in pdf_paths:
            pdf_results: list[ExtractionResult] = []
            for tool_name in options.tool_names:
                result = self._run_with_cache(pdf_path, tool_name)
                pdf_results.append(result)
                comparativo.append(result.to_summary())
            results.append(pdf_results)

        summary_path = self.artifact_dir / "comparativo.json"
        payload = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "runs": comparativo,
        }
        summary_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return results

    def run_single(self, pdf_path: Path, options: ExtractionOptions | None = None) -> ExtractionResult:
        """Processa um único PDF usando apenas a primeira ferramenta da lista."""
        options = options or ExtractionOptions.defaults()
        options.validate()
        tool_name = options.tool_names[0]
        return self._run_with_cache(pdf_path, tool_name)

    # Internal helpers -----------------------------------------------------------------

    def _run_with_cache(self, pdf_path: Path, tool_name: str) -> ExtractionResult:
        """Executa a ferramenta, reutilizando resultados persistidos quando disponíveis."""
        artifact_dir = self._artifact_dir_for(pdf_path, tool_name)
        if not self.overwrite and self._has_cached_summary(artifact_dir):
            cached = self._load_cached_result(pdf_path, tool_name, artifact_dir)
            if cached:
                return cached
        start = time.perf_counter()
        error_message: str | None = None
        success = True
        try:
            adapter = self._get_adapter(tool_name)
            bundle = adapter.extract(pdf_path)
        except AdapterRuntimeError as exc:
            success = False
            error_message = str(exc)
            bundle = ExtractionBundle(
                text=f"Falha na ferramenta {tool_name}: {error_message}",
                tables=[],
                figures=[],
                metadata={"error": error_message, "tool": tool_name},
            )
        except Exception as exc:  # pragma: no cover - fallback
            success = False
            error_message = f"Erro inesperado: {exc}"
            bundle = ExtractionBundle(
                text=f"Erro inesperado durante {tool_name}: {exc}",
                tables=[],
                figures=[],
                metadata={"error": error_message, "tool": tool_name},
            )
        elapsed = time.perf_counter() - start

        metrics = ExtractionMetrics(
            pdf_name=pdf_path.name,
            tool_name=tool_name,
            elapsed_seconds=elapsed,
            text_characters=len(bundle.text or ""),
            tables_count=len(bundle.tables),
            figures_count=len(bundle.figures),
            table_quality=estimate_table_quality(bundle.tables),
            notes=error_message or "",
            success=success,
        )
        result = ExtractionResult(
            pdf_path=pdf_path,
            tool_name=tool_name,
            bundle=bundle,
            metrics=metrics,
            artifact_dir=artifact_dir,
            error=error_message,
        )
        self._persist_result(result)
        return result

    def _get_adapter(self, tool_name: str) -> ToolAdapter:
        """Obtém adaptador do cache ou instancia dinamicamente."""
        if tool_name in self._adapter_cache:
            return self._adapter_cache[tool_name]
        adapter_cls = ADAPTER_TYPES.get(tool_name)
        if not adapter_cls:
            raise ValueError(f"Ferramenta não suportada: {tool_name}")
        try:
            adapter = adapter_cls()
        except AdapterRuntimeError:
            raise
        except Exception as exc:  # pragma: no cover - defensive
            raise AdapterRuntimeError(
                f"Falha ao inicializar adaptador {tool_name}: {exc}"
            ) from exc
        self._adapter_cache[tool_name] = adapter
        return adapter

    def _artifact_dir_for(self, pdf_path: Path, tool_name: str) -> Path:
        """Calcula caminho onde os artefatos desse PDF/ferramenta serão salvos."""
        pdf_dir = self.artifact_dir / pdf_path.stem / tool_name
        return pdf_dir

    def _persist_result(self, result: ExtractionResult) -> None:
        """Grava texto, tabelas, figuras e resumo em disco para reutilização posterior."""
        artifact_dir = result.artifact_dir
        if artifact_dir.exists() and self.overwrite:
            shutil.rmtree(artifact_dir)
        artifact_dir.mkdir(parents=True, exist_ok=True)

        (artifact_dir / "text.md").write_text(result.bundle.text or "", encoding="utf-8")
        tables_payload = [table.to_dict() for table in result.bundle.tables]
        (artifact_dir / "tables.json").write_text(
            json.dumps(tables_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        figures_payload = [figure.to_dict() for figure in result.bundle.figures]
        (artifact_dir / "figures.json").write_text(
            json.dumps(figures_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        summary = result.to_summary()
        (artifact_dir / "summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _has_cached_summary(self, artifact_dir: Path) -> bool:
        """Verifica se já existe um summary.json no diretório de artefatos."""
        return (artifact_dir / "summary.json").exists()

    def _load_cached_result(
        self, pdf_path: Path, tool_name: str, artifact_dir: Path
    ) -> ExtractionResult | None:
        """Reconstrói um ExtractionResult a partir dos arquivos já persistidos."""
        summary_path = artifact_dir / "summary.json"
        try:
            summary_data = json.loads(summary_path.read_text(encoding="utf-8"))
        except Exception:
            return None

        metrics = ExtractionMetrics(
            pdf_name=summary_data.get("pdf_name", pdf_path.name),
            tool_name=tool_name,
            elapsed_seconds=summary_data.get("elapsed_seconds", 0.0),
            text_characters=summary_data.get("text_characters", 0),
            tables_count=summary_data.get("tables_count", 0),
            figures_count=summary_data.get("figures_count", 0),
            table_quality=summary_data.get("table_quality", 0.0),
            notes=summary_data.get("notes", ""),
            success=summary_data.get("success", True),
        )
        text = (artifact_dir / "text.md").read_text(encoding="utf-8") if (artifact_dir / "text.md").exists() else ""
        tables = self._load_tables(artifact_dir / "tables.json")
        figures = self._load_figures(artifact_dir / "figures.json")
        bundle = ExtractionBundle(
            text=text,
            tables=tables,
            figures=figures,
            metadata=summary_data.get("metadata", {}),
        )
        return ExtractionResult(
            pdf_path=pdf_path,
            tool_name=tool_name,
            bundle=bundle,
            metrics=metrics,
            artifact_dir=artifact_dir,
            error=summary_data.get("error"),
        )

    def _load_tables(self, path: Path) -> list[TableArtifact]:
        """Converte o JSON de tabelas em objetos TableArtifact."""
        if not path.exists():
            return []
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return []
        tables: list[TableArtifact] = []
        for table in payload:
            tables.append(
                TableArtifact(
                    rows=table.get("rows", []),
                    caption=table.get("caption"),
                    page=table.get("page"),
                    metadata=table.get("metadata", {}),
                )
            )
        return tables

    def _load_figures(self, path: Path) -> list[FigureArtifact]:
        """Converte o JSON de figuras em objetos FigureArtifact."""
        if not path.exists():
            return []
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return []
        figures: list[FigureArtifact] = []
        for figure in payload:
            figures.append(
                FigureArtifact(
                    caption=figure.get("caption"),
                    page=figure.get("page"),
                    description=figure.get("description"),
                    metadata=figure.get("metadata", {}),
                )
            )
        return figures

