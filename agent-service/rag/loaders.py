from __future__ import annotations

import re
from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path
from typing import Iterable, TypeAlias

import pymupdf
from docx import Document


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}
MetadataValue: TypeAlias = str | int | float | bool


@dataclass(frozen=True)
class TextUnit:
    """Một đơn vị văn bản giữ nguyên ranh giới trang khi có thể."""

    source_path: str
    source_name: str
    file_type: str
    text: str
    page: int
    metadata: dict[str, MetadataValue] = field(default_factory=dict)


def clean_text(text: str) -> str:
    """Chuẩn hóa khoảng trắng nhưng vẫn giữ ranh giới đoạn văn."""

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"(?<=\w)-\n(?=\w)", "", text)
    lines = [re.sub(r"[\t ]+", " ", line).strip() for line in text.split("\n")]

    normalized: list[str] = []
    previous_blank = False
    for line in lines:
        if not line:
            if normalized and not previous_blank:
                normalized.append("")
            previous_blank = True
            continue
        normalized.append(line)
        previous_blank = False

    return "\n".join(normalized).strip()


def discover_documents(root: Path) -> list[Path]:
    if not root.exists():
        raise FileNotFoundError(f"Không tìm thấy thư mục dữ liệu: {root}")
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def _relative_source(path: Path, data_root: Path) -> str:
    try:
        return path.resolve().relative_to(data_root.resolve()).as_posix()
    except ValueError:
        return path.name


def _load_pdf_bytes(
    content: bytes,
    source_path: str,
    source_name: str,
    metadata: dict[str, MetadataValue],
) -> Iterable[TextUnit]:
    with pymupdf.open(stream=content, filetype="pdf") as pdf:
        for page_index, page in enumerate(pdf, start=1):
            text = clean_text(page.get_text("text", sort=True))
            if text:
                yield TextUnit(source_path, source_name, "pdf", text, page_index, metadata.copy())


def _load_docx_bytes(
    content: bytes,
    source_path: str,
    source_name: str,
    metadata: dict[str, MetadataValue],
) -> Iterable[TextUnit]:
    document = Document(BytesIO(content))
    paragraphs = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]
    text = clean_text("\n\n".join(paragraphs))
    if text:
        yield TextUnit(source_path, source_name, "docx", text, 0, metadata.copy())


def _load_text_bytes(
    content: bytes,
    source_path: str,
    source_name: str,
    file_type: str,
    metadata: dict[str, MetadataValue],
) -> Iterable[TextUnit]:
    try:
        raw = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        raw = content.decode("utf-8", errors="replace")
    text = clean_text(raw)
    if text:
        yield TextUnit(source_path, source_name, file_type, text, 0, metadata.copy())


def load_document_bytes(
    content: bytes,
    filename: str,
    *,
    source_path: str | None = None,
    metadata: dict[str, MetadataValue] | None = None,
) -> list[TextUnit]:
    """Load an Odoo attachment or other in-memory document without a temp file."""

    if not content:
        raise ValueError("Nội dung tài liệu đang rỗng")
    safe_name = Path(filename).name
    suffix = Path(safe_name).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Định dạng chưa được hỗ trợ: {suffix or safe_name}")

    resolved_source = source_path or safe_name
    extra_metadata = dict(metadata or {})
    if suffix == ".pdf":
        return list(_load_pdf_bytes(content, resolved_source, safe_name, extra_metadata))
    if suffix == ".docx":
        return list(_load_docx_bytes(content, resolved_source, safe_name, extra_metadata))
    return list(
        _load_text_bytes(
            content,
            resolved_source,
            safe_name,
            suffix.lstrip("."),
            extra_metadata,
        )
    )


def load_document(path: Path, data_root: Path) -> list[TextUnit]:
    return load_document_bytes(
        path.read_bytes(),
        path.name,
        source_path=_relative_source(path, data_root),
    )
