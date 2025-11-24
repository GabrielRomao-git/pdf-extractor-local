"""Ferramentas compartilhadas para extração de conteúdo em PDFs acadêmicos."""

from importlib import metadata


def __get_version() -> str:
    try:
        return metadata.version("pdf-extractor-local")
    except metadata.PackageNotFoundError:  # pragma: no cover
        return "0.0.0"


__version__ = __get_version()

__all__ = ["__version__"]
