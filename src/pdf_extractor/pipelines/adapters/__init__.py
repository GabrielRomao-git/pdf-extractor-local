"""Coleção de adaptadores suportados."""

from .chandra_adapter import ChandraAdapter
from .docling_adapter import DoclingAdapter
from .grobid_adapter import GrobidAdapter
from .marker_adapter import MarkerAdapter
from .markitdown_adapter import MarkitdownAdapter
from .nougat_adapter import NougatAdapter
from .pdfplumber_adapter import PdfPlumberAdapter
from .pymupdf_adapter import PyMuPDFAdapter

ADAPTER_TYPES = {
    adapter.name: adapter
    for adapter in [
        ChandraAdapter,
        DoclingAdapter,
        MarkitdownAdapter,
        PyMuPDFAdapter,
        PdfPlumberAdapter,
        GrobidAdapter,
        NougatAdapter,
        MarkerAdapter,
    ]
}

__all__ = [
    "ADAPTER_TYPES",
    "ChandraAdapter",
    "DoclingAdapter",
    "MarkitdownAdapter",
    "PyMuPDFAdapter",
    "PdfPlumberAdapter",
    "GrobidAdapter",
    "NougatAdapter",
    "MarkerAdapter",
]

