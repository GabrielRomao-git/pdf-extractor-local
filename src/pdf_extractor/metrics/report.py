from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class RunMetric:
    pdf_name: str
    tool: str
    elapsed_seconds: float
    text_characters: int
    char_percent: float
    tables_count: int
    table_quality: float
    figures_count: int
    notes: str
    success: bool
    artifact_dir: str


class ComparativeReport:
    def __init__(self, runs: list[RunMetric], generated_at: str | None = None) -> None:
        self.runs = runs
        self.generated_at = generated_at

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "ComparativeReport":
        runs_payload = payload.get("runs", [])
        pdf_totals: dict[str, int] = defaultdict(int)
        for item in runs_payload:
            pdf_name = item.get("pdf_name")
            chars = item.get("text_characters", 0)
            pdf_totals[pdf_name] = max(pdf_totals[pdf_name], chars)

        runs: list[RunMetric] = []
        for item in runs_payload:
            pdf_name = item.get("pdf_name")
            max_chars = pdf_totals.get(pdf_name, 0) or 1
            char_percent = round(
                (item.get("text_characters", 0) / max_chars) * 100, 2
            )
            runs.append(
                RunMetric(
                    pdf_name=pdf_name,
                    tool=item.get("tool"),
                    elapsed_seconds=item.get("elapsed_seconds", 0.0),
                    text_characters=item.get("text_characters", 0),
                    char_percent=char_percent,
                    tables_count=item.get("tables_count", 0),
                    table_quality=item.get("table_quality", 0.0),
                    figures_count=item.get("figures_count", 0),
                    notes=item.get("notes", ""),
                    success=item.get("success", True),
                    artifact_dir=item.get("artifact_dir", ""),
                )
            )
        return cls(runs=runs, generated_at=payload.get("generated_at"))

    # --------------------------------------------------------------------- Rendering

    def to_markdown(self) -> str:
        rec = self.recommendation()
        lines = [
            "# Comparativo de Ferramentas",
            f"_Gerado em {self.generated_at or '-'}_",
            "",
            "## Recomendação",
            f"- 1ª escolha: **{rec['primary']}**",
            f"- Fallbacks: {', '.join(rec['fallbacks']) or 'n/a'}",
            "",
            "## Ranking por Ferramenta",
            self._render_tool_table(),
            "",
            "## Detalhes por PDF",
        ]
        for pdf in self.pdf_names:
            lines.append(f"### {pdf}")
            lines.append(self._render_pdf_table(pdf))
            lines.append("")
        return "\n".join(lines).strip() + "\n"

    # --------------------------------------------------------------------- Helpers

    @property
    def pdf_names(self) -> list[str]:
        return sorted({run.pdf_name for run in self.runs})

    def recommendation(self) -> dict[str, list[str] | str]:
        by_tool = self._aggregate_by_tool()
        ranking = sorted(
            by_tool.values(),
            key=lambda item: (
                item["char_percent_avg"],
                item["table_quality_avg"],
                item["success_rate"],
                -item["elapsed_avg"],
            ),
            reverse=True,
        )
        if not ranking:
            return {"primary": "n/a", "fallbacks": []}
        primary = ranking[0]["tool"]
        fallbacks = [entry["tool"] for entry in ranking[1:3]]
        return {"primary": primary, "fallbacks": fallbacks}

    def _aggregate_by_tool(self) -> dict[str, dict[str, Any]]:
        aggregation: dict[str, dict[str, Any]] = {}
        for run in self.runs:
            agg = aggregation.setdefault(
                run.tool,
                {
                    "tool": run.tool,
                    "elapsed_total": 0.0,
                    "entries": 0,
                    "char_percent_total": 0.0,
                    "table_quality_total": 0.0,
                    "success_total": 0,
                },
            )
            agg["elapsed_total"] += run.elapsed_seconds
            agg["char_percent_total"] += run.char_percent
            agg["table_quality_total"] += run.table_quality * 100
            agg["entries"] += 1
            agg["success_total"] += 1 if run.success else 0

        for agg in aggregation.values():
            entries = max(agg["entries"], 1)
            agg["elapsed_avg"] = agg["elapsed_total"] / entries
            agg["char_percent_avg"] = agg["char_percent_total"] / entries
            agg["table_quality_avg"] = agg["table_quality_total"] / entries
            agg["success_rate"] = (agg["success_total"] / entries) * 100
        return aggregation

    def _render_tool_table(self) -> str:
        by_tool = self._aggregate_by_tool()
        headers = [
            "Ferramenta",
            "Tempo médio (s)",
            "% texto médio",
            "Qualidade tabelas",
            "Sucesso (%)",
        ]
        rows = []
        for tool in sorted(by_tool.values(), key=lambda item: item["tool"]):
            rows.append(
                [
                    tool["tool"],
                    f"{tool['elapsed_avg']:.2f}",
                    f"{tool['char_percent_avg']:.1f}%",
                    f"{tool['table_quality_avg']:.1f}%",
                    f"{tool['success_rate']:.1f}%",
                ]
            )
        return self._format_table(headers, rows)

    def _render_pdf_table(self, pdf_name: str) -> str:
        headers = ["Ferramenta", "Tempo (s)", "% texto", "Tabelas", "Figuras", "Notas"]
        rows = []
        for run in sorted(
            (r for r in self.runs if r.pdf_name == pdf_name),
            key=lambda r: r.char_percent,
            reverse=True,
        ):
            rows.append(
                [
                    run.tool,
                    f"{run.elapsed_seconds:.2f}",
                    f"{run.char_percent:.1f}%",
                    f"{run.tables_count} ({run.table_quality*100:.0f}%)",
                    str(run.figures_count),
                    run.notes or "-",
                ]
            )
        return self._format_table(headers, rows)

    def _format_table(self, headers: list[str], rows: list[list[str]]) -> str:
        if not rows:
            return "_Sem dados disponíveis._"
        header_line = "| " + " | ".join(headers) + " |"
        separator = "| " + " | ".join("---" for _ in headers) + " |"
        body = "\n".join("| " + " | ".join(row) + " |" for row in rows)
        return "\n".join([header_line, separator, body])

