from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from pdf_extractor.pipelines.base import AdapterRuntimeError, ExtractionBundle, ToolAdapter
from pdf_extractor.pipelines.adapters.markitdown_adapter import extract_tables_from_markdown


class NougatAdapter(ToolAdapter):
    name = "nougat"
    display_name = "Nougat OCR"
    description = "Cli Nougat para converter PDFs científicos em Markdown"

    def __init__(self, command: str | None = None, model: str | None = None) -> None:
        self.command = command or os.getenv("NOUGAT_CLI", "nougat")
        self.model = model or os.getenv("NOUGAT_MODEL", "0.1.0-base")

    def extract(self, pdf_path: Path) -> ExtractionBundle:
        cli_path = shutil.which(self.command)
        if not cli_path:
            raise AdapterRuntimeError(
                f"CLI do Nougat ({self.command}) não encontrado no PATH."
            )

        with tempfile.TemporaryDirectory(prefix="nougat-") as tmpdir:
            output_dir = Path(tmpdir)
            cmd = [
                cli_path,
                str(pdf_path),
                "-o",
                str(output_dir),
                "--model",
                self.model,
                "--markdown",
            ]
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
            )
            if process.returncode != 0:
                raise AdapterRuntimeError(
                    f"Nougat retornou código {process.returncode}: {process.stderr.strip()}"
                )

            markdown_files = sorted(output_dir.glob("*.md"))
            if not markdown_files:
                raise AdapterRuntimeError("Nougat não gerou arquivos Markdown.")
            text = markdown_files[0].read_text(encoding="utf-8")

        tables = extract_tables_from_markdown(text)
        metadata = {
            "engine": "nougat",
            "command": self.command,
            "model": self.model,
        }
        return ExtractionBundle(text=text, tables=tables, figures=[], metadata=metadata)

