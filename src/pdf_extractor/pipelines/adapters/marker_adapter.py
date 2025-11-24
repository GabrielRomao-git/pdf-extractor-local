from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import tempfile
from pathlib import Path

from pdf_extractor.pipelines.base import AdapterRuntimeError, ExtractionBundle, ToolAdapter
from pdf_extractor.pipelines.adapters.markitdown_adapter import extract_tables_from_markdown


class MarkerAdapter(ToolAdapter):
    name = "marker"
    display_name = "Marker PDF"
    description = "CLI Marker para extração multimodal"

    RETRYABLE_CODES = {-7, -8, -9}

    def __init__(self, command: str | None = None) -> None:
        # O CLI `marker` padrão usa multiprocessamento intenso e falha facilmente em CPU,
        # então priorizamos `marker_single`, conforme README oficial.
        self.command = command or os.getenv("MARKER_CLI", "marker_single")
        self.max_retries = int(os.getenv("MARKER_MAX_RETRIES", "1"))
        self.batch_multiplier = os.getenv("MARKER_BATCH_MULTIPLIER", "1")
        self.extra_args = shlex.split(os.getenv("MARKER_EXTRA_ARGS", ""))
        self.use_uv_run = os.getenv("MARKER_USE_UV_RUN", "1") != "0"
        self.uv_binary = os.getenv("MARKER_UV_BINARY", "uv")

    def extract(self, pdf_path: Path) -> ExtractionBundle:
        base_cmd: list[str]
        if self.use_uv_run:
            uv_path = shutil.which(self.uv_binary)
            if not uv_path:
                raise AdapterRuntimeError(
                    f"UV ({self.uv_binary}) não encontrado para executar marker."
                )
            base_cmd = [uv_path, "run", self.command]
        else:
            cli_path = shutil.which(self.command)
            if not cli_path:
                raise AdapterRuntimeError(
                    f"CLI do Marker ({self.command}) não encontrado."
                )
            base_cmd = [cli_path]

        markdown: str | None = None
        warning_message: str | None = None
        attempts = self.max_retries + 1
        last_error = ""
        attempt_index = 0

        for attempt_index in range(1, attempts + 1):
            with tempfile.TemporaryDirectory(prefix="marker-") as tmpdir:
                tmp = Path(tmpdir)
                output_dir = tmp / "output"
                output_dir.mkdir(parents=True, exist_ok=True)
                cmd = [
                    *base_cmd,
                    str(pdf_path),
                    str(output_dir),
                ]
                cmd.extend(["--batch_multiplier", self.batch_multiplier])
                if self.extra_args:
                    cmd.extend(self.extra_args)
                env = os.environ.copy()
                env.setdefault("PYTHONFAULTHANDLER", "1")
                env.setdefault("MARKER_LOG_LEVEL", "DEBUG")
                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=False,
                    env=env,
                )

                markdown_files = sorted(output_dir.rglob("*.md"))
                has_markdown = bool(markdown_files)
                if has_markdown:
                    markdown = markdown_files[0].read_text(encoding="utf-8")

                if process.returncode == 0 and has_markdown:
                    break

                if has_markdown and process.returncode != 0:
                    warning_message = (
                        f"Marker retornou código {process.returncode}, mas produziu Markdown."
                    )
                    break

                last_error = (
                    process.stderr.strip()
                    or process.stdout.strip()
                    or f"Código {process.returncode}"
                )
                if (
                    process.returncode in self.RETRYABLE_CODES
                    and attempt_index < attempts
                ):
                    continue
                raise AdapterRuntimeError(
                    f"Marker retornou código {process.returncode}: {last_error}"
                )

        if markdown is None:
            raise AdapterRuntimeError(
                f"Marker não produziu Markdown após {attempts} tentativas: {last_error}"
            )

        tables = extract_tables_from_markdown(markdown)
        metadata = {
            "engine": "marker",
            "command": self.command,
            "attempts": attempt_index,
        }
        if warning_message:
            metadata["warning"] = warning_message
        return ExtractionBundle(text=markdown, tables=tables, figures=[], metadata=metadata)

