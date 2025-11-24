from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional

import click
from rich.console import Console

from pdf_extractor.pipelines.manager import ExtractionManager, ExtractionOptions

console = Console()


def _load_default_pdfs(input_dir: Path) -> list[Path]:
    if not input_dir.exists():
        raise click.BadParameter(f"Pasta {input_dir} não encontrada")
    return sorted(path for path in input_dir.iterdir() if path.suffix.lower() == ".pdf")


@click.group(help="Ferramenta para extrair e avaliar conteúdos de PDFs acadêmicos.")
def app() -> None:
    """CLI raiz."""


@app.command()
@click.option(
    "--pdf-dir",
    "-p",
    type=click.Path(path_type=Path, exists=True, dir_okay=True, file_okay=False),
    default=Path("pdfs-reais"),
    show_default=True,
    help="Diretório contendo os PDFs de entrada.",
)
@click.option(
    "--artifact-dir",
    "-a",
    type=click.Path(path_type=Path, dir_okay=True, file_okay=False),
    default=Path("artifacts"),
    show_default=True,
    help="Diretório onde as saídas serão salvas.",
)
@click.option(
    "--tools",
    "-t",
    type=str,
    default=None,
    help=(
        "Lista separada por vírgula com os adaptadores a serem executados "
        "(ex: docling,markitdown). Padrão: todos suportados."
    ),
)
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    show_default=True,
    help="Sobrescrever saídas existentes.",
)
def extract(pdf_dir: Path, artifact_dir: Path, tools: Optional[str], overwrite: bool) -> None:
    """Executa a extração padronizada para todos os PDFs e ferramentas selecionadas."""
    pdfs = _load_default_pdfs(pdf_dir)
    options = ExtractionOptions.from_tool_list(tools)
    manager = ExtractionManager(artifact_dir=artifact_dir, overwrite=overwrite)
    with console.status("Executando pipelines de extração..."):
        results = manager.run_batch(pdfs, options)
    console.print(f"Processamento concluído para {len(results)} PDFs.")


@app.command()
@click.option(
    "--report-path",
    "-r",
    type=click.Path(path_type=Path, exists=True, dir_okay=False),
    default=Path("artifacts/comparativo.json"),
    show_default=True,
    help="Arquivo JSON a ser usado para gerar métricas e tabelas comparativas.",
)
@click.option(
    "--output-markdown",
    "-m",
    type=click.Path(path_type=Path, dir_okay=False, file_okay=True),
    default=Path("docs/comparativo.md"),
    show_default=True,
    help="Arquivo markdown com resumo das métricas.",
)
def evaluate(report_path: Path, output_markdown: Path) -> None:
    """Gera relatório consolidado de métricas a partir das saídas das ferramentas."""
    data = json.loads(report_path.read_text(encoding="utf-8"))
    from pdf_extractor.metrics.report import ComparativeReport

    report = ComparativeReport.from_payload(data)
    md = report.to_markdown()
    output_markdown.parent.mkdir(parents=True, exist_ok=True)
    output_markdown.write_text(md, encoding="utf-8")
    console.print(f"Relatório salvo em {output_markdown}")


@app.command()
@click.option(
    "--pdf",
    "-p",
    type=click.Path(path_type=Path, exists=True, dir_okay=False),
    default=Path(
        "pdfs-reais/DM - Diet and exercise in the prevention and treatment of type 2 diabetes mellitus.pdf"  # noqa: E501
    ),
    show_default=True,
    help="PDF usado na demonstração rápida.",
)
@click.option(
    "--tool",
    "-t",
    type=str,
    default="docling",
    show_default=True,
    help="Ferramenta destacada para a demo.",
)
@click.option(
    "--artifact-dir",
    "-a",
    type=click.Path(path_type=Path, dir_okay=True, file_okay=False),
    default=Path("artifacts/demo"),
    show_default=True,
    help="Saída da demo.",
)
def demo(pdf: Path, tool: str, artifact_dir: Path) -> None:
    """Executa uma demo rápida em um único PDF e produz saída Markdown resumida."""
    manager = ExtractionManager(artifact_dir=artifact_dir, overwrite=True)
    options = ExtractionOptions.from_tool_list(tool)
    start = time.perf_counter()
    result = manager.run_single(pdf, options)
    elapsed = time.perf_counter() - start
    markdown_path = artifact_dir / f"{pdf.stem}-{tool}.md"
    markdown_path.write_text(result.to_markdown(), encoding="utf-8")
    console.print(f"Demo pronta ({elapsed:.2f}s). Resultado em {markdown_path}.")


if __name__ == "__main__":  # pragma: no cover
    app()

