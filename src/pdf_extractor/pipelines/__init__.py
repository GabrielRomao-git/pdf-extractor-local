"""Pipelines de extração padronizados."""

from .base import ExtractionBundle, ExtractionResult, FigureArtifact, TableArtifact
from .manager import ExtractionManager, ExtractionOptions

__all__ = [
    "ExtractionBundle",
    "ExtractionResult",
    "FigureArtifact",
    "TableArtifact",
    "ExtractionManager",
    "ExtractionOptions",
]
