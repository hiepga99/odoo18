from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pymupdf
from docx import Document


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


@dataclass(frozen=True)
class TextUnit:
    """Một đơn vị văn bản giữ nguyên ranh giới trang khi có thể."""

    source_path: str
    source_name: str
    file_type: str
    text: str
    page: int


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


def _load_pdf(path: Path, data_root: Path) -> Iterable[TextUnit]:
    source_path = _relative_source(path, data_root)
    with pymupdf.open(path) as pdf:
        for page_index, page in enumerate(pdf, start=1):
            text = clean_text(page.get_text("text", sort=True))
            if text:
                yield TextUnit(source_path, path.name, "pdf", text, page_index)


def _load_docx(path: Path, data_root: Path) -> Iterable[TextUnit]:
    document = Document(path)
    paragraphs = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]
    text = clean_text("\n\n".join(paragraphs))
    if text:
        yield TextUnit(_relative_source(path, data_root), path.name, "docx", text, 0)


def _load_text(path: Path, data_root: Path) -> Iterable[TextUnit]:
    try:
        raw = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        raw = path.read_text(encoding="utf-8", errors="replace")
    text = clean_text(raw)
    if text:
        yield TextUnit(
            _relative_source(path, data_root),
            path.name,
            path.suffix.lower().lstrip("."),
            text,
            0,
        )


def load_document(path: Path, data_root: Path) -> list[TextUnit]:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return list(_load_pdf(path, data_root))
    if suffix == ".docx":
        return list(_load_docx(path, data_root))
    if suffix in {".txt", ".md"}:
        return list(_load_text(path, data_root))
    raise ValueError(f"Định dạng chưa được hỗ trợ: {path}")
