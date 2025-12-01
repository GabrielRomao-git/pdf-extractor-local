from __future__ import annotations

import base64
import io
import os
from pathlib import Path
from typing import Callable, Iterable

from bs4 import BeautifulSoup

from pdf_extractor.pipelines.base import (
    AdapterRuntimeError,
    ExtractionBundle,
    FigureArtifact,
    TableArtifact,
    ToolAdapter,
)


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value not in {"0", "false", "False"}


def _env_int(name: str, default: int | None) -> int | None:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    try:
        return int(value)
    except ValueError:
        return default


class ChandraAdapter(ToolAdapter):
    name = "chandra"
    display_name = "Chandra OCR"
    description = "Integração direta com o InferenceManager oficial do Chandra."

    def __init__(self, method: str | None = None) -> None:
        """Carrega o InferenceManager e configurações a partir das variáveis CHANDRA_*."""
        try:
            from chandra.input import load_file as chandra_load_file
            from chandra.model import InferenceManager
            from chandra.model.schema import BatchInputItem
        except Exception as exc:  # pragma: no cover - depende de instalação externa
            raise AdapterRuntimeError(
                "Chandra não está instalado. Consulte o README para instalação por source."
            ) from exc

        self._load_file: Callable[..., list] = chandra_load_file
        self._batch_item = BatchInputItem

        self.method = (method or os.getenv("CHANDRA_METHOD", "vllm")).lower()
        self.batch_size = _env_int(
            "CHANDRA_BATCH_SIZE",
            28 if self.method == "vllm" else 1,
        )
        self.prompt_type = os.getenv("CHANDRA_PROMPT_TYPE", "ocr_layout")
        self.include_images = _env_bool("CHANDRA_INCLUDE_IMAGES", True)
        self.include_headers = _env_bool("CHANDRA_INCLUDE_HEADERS", False)
        self.max_output_tokens = _env_int("CHANDRA_MAX_OUTPUT_TOKENS", None)
        self.max_workers = _env_int("CHANDRA_MAX_WORKERS", None)
        self.max_retries = _env_int("CHANDRA_MAX_RETRIES", None)
        self.page_range = os.getenv("CHANDRA_PAGE_RANGE")
        self.vllm_api_base = os.getenv("CHANDRA_VLLM_API_BASE")
        self.bbox_scale = _env_int("CHANDRA_BBOX_SCALE", None)

        try:
            self._manager = InferenceManager(method=self.method)
        except Exception as exc:  # pragma: no cover - inicialização pesada
            raise AdapterRuntimeError(f"Falha ao inicializar o Chandra ({self.method}): {exc}") from exc

    def extract(self, pdf_path: Path) -> ExtractionBundle:
        """Processa o PDF diretamente via InferenceManager e organiza a saída."""
        images = self._load_document_images(pdf_path)
        if not images:
            raise AdapterRuntimeError(f"Chandra não retornou páginas para {pdf_path.name}.")

        assembled_text: list[str] = []
        tables: list[TableArtifact] = []
        figures: list[FigureArtifact] = []
        pages_metadata: list[dict[str, object]] = []

        page_counter = 0
        for batch in self._yield_batches(images, self.batch_size or 1):
            outputs = self._run_inference(batch)
            for output in outputs:
                page_counter += 1
                if output.error:
                    raise AdapterRuntimeError(f"Chandra retornou erro na página {page_counter}.")
                assembled_text.append(self._format_page_markdown(output.markdown, page_counter))
                tables.extend(self._extract_tables(output.html, page_counter))
                figures.extend(self._extract_figures(output, page_counter))
                pages_metadata.append(
                    {
                        "page": page_counter,
                        "token_count": output.token_count,
                        "chunks": len(output.chunks or []),
                    }
                )

        metadata = {
            "engine": "chandra",
            "method": self.method,
            "batch_size": self.batch_size,
            "include_images": self.include_images,
            "include_headers": self.include_headers,
            "pages": pages_metadata,
        }
        if self.page_range:
            metadata["page_range"] = self.page_range

        text = "\n\n".join(assembled_text).strip()
        return ExtractionBundle(text=text, tables=tables, figures=figures, metadata=metadata)

    # Helpers -------------------------------------------------------------------------

    def _load_document_images(self, pdf_path) -> list:
        config = {"page_range": self.page_range} if self.page_range else {}
        try:
            return self._load_file(str(pdf_path), config)
        except Exception as exc:
            raise AdapterRuntimeError(f"Chandra falhou ao carregar {pdf_path.name}: {exc}") from exc

    def _yield_batches(self, items: list, batch_size: int) -> Iterable[list]:
        for start in range(0, len(items), batch_size):
            yield items[start : start + batch_size]

    def _run_inference(self, images_batch: list) -> list:
        batch = [self._batch_item(image=image, prompt_type=self.prompt_type) for image in images_batch]
        generate_kwargs: dict[str, object] = {
            "include_images": self.include_images,
            "include_headers_footers": self.include_headers,
        }
        if self.max_output_tokens:
            generate_kwargs["max_output_tokens"] = self.max_output_tokens
        if self.method == "vllm":
            if self.max_workers:
                generate_kwargs["max_workers"] = self.max_workers
            if self.max_retries:
                generate_kwargs["max_retries"] = self.max_retries
            if self.vllm_api_base:
                generate_kwargs["vllm_api_base"] = self.vllm_api_base
        if self.bbox_scale:
            generate_kwargs["bbox_scale"] = self.bbox_scale

        try:
            return self._manager.generate(batch, **generate_kwargs)
        except Exception as exc:
            raise AdapterRuntimeError(f"Chandra falhou durante a inferência: {exc}") from exc

    def _format_page_markdown(self, markdown: str, page_number: int) -> str:
        header = f"\n\n## Página {page_number}\n\n"
        cleaned = (markdown or "").strip()
        return f"{header}{cleaned}" if cleaned else header

    def _extract_tables(self, html: str, page_number: int) -> list[TableArtifact]:
        if not html:
            return []
        soup = BeautifulSoup(html, "html.parser")
        tables: list[TableArtifact] = []
        for idx, table_tag in enumerate(soup.find_all("table")):
            rows: list[list[str]] = []
            for row in table_tag.find_all("tr"):
                cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["td", "th"])]
                if cells:
                    rows.append(cells)
            caption_tag = table_tag.find("caption")
            caption = caption_tag.get_text(" ", strip=True) if caption_tag else None
            tables.append(
                TableArtifact(
                    rows=rows,
                    caption=caption or None,
                    page=page_number,
                    metadata={"idx": idx, "source": "chandra"},
                )
            )
        return tables

    def _extract_figures(self, output, page_number: int) -> list[FigureArtifact]:
        figures: list[FigureArtifact] = []
        images_iter = iter((output.images or {}).items())
        chunks = output.chunks or []
        for idx, chunk in enumerate(chunks):
            label = chunk.get("label")
            if label not in {"Image", "Figure"}:
                continue
            caption = BeautifulSoup(chunk.get("content") or "", "html.parser").get_text(" ", strip=True) or None
            metadata = {
                "idx": idx,
                "label": label,
                "bbox": chunk.get("bbox"),
            }
            try:
                image_name, pil_image = next(images_iter)
                metadata["image_name"] = image_name
                metadata["image_base64"] = self._pil_to_base64(pil_image)
            except StopIteration:
                pass
            figures.append(
                FigureArtifact(
                    caption=caption,
                    page=page_number,
                    description=None,
                    metadata=metadata,
                )
            )
        return figures

    def _pil_to_base64(self, image) -> str:
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("ascii")

