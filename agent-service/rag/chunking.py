from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field

from .loaders import MetadataValue, TextUnit


@dataclass(frozen=True)
class Chunk:
    id: str
    text: str
    source_path: str
    source_name: str
    file_type: str
    page: int
    chunk_index: int
    document_hash: str
    extra_metadata: dict[str, MetadataValue] = field(default_factory=dict)

    def metadata(self) -> dict[str, MetadataValue]:
        # Core values win over caller metadata so citations cannot be corrupted.
        return {
            **self.extra_metadata,
            "source_path": self.source_path,
            "source_name": self.source_name,
            "file_type": self.file_type,
            "page": self.page,
            "chunk_index": self.chunk_index,
            "document_hash": self.document_hash,
            "char_count": len(self.text),
        }


def _choose_boundary(text: str, start: int, hard_end: int, chunk_size: int) -> int:
    if hard_end >= len(text):
        return len(text)

    min_end = min(hard_end, start + max(int(chunk_size * 0.60), 1))
    window = text[min_end:hard_end]

    candidates: list[int] = []
    for match in re.finditer(r"\n\n|(?<=[.!?…:;])\s+|\n|\s+", window):
        candidates.append(min_end + match.end())
    return candidates[-1] if candidates else hard_end


def split_text(text: str, chunk_size: int = 1000, overlap: int = 150) -> list[str]:
    if chunk_size < 100:
        raise ValueError("chunk_size phải từ 100 ký tự trở lên")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("chunk_overlap phải >= 0 và nhỏ hơn chunk_size")

    text = text.strip()
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        hard_end = min(start + chunk_size, len(text))
        end = _choose_boundary(text, start, hard_end, chunk_size)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break

        next_start = max(0, end - overlap)
        if next_start > start:
            whitespace = re.search(r"\s", text[next_start:end])
            if whitespace:
                next_start += whitespace.end()
        if next_start <= start:
            next_start = end
        start = next_start

    return chunks


def chunk_units(
    units: list[TextUnit],
    chunk_size: int = 1000,
    overlap: int = 150,
) -> list[Chunk]:
    chunks: list[Chunk] = []
    per_source_index: dict[str, int] = {}

    for unit in units:
        document_hash = hashlib.sha256(
            f"{unit.source_path}\n{unit.text}".encode("utf-8")
        ).hexdigest()
        for text in split_text(unit.text, chunk_size=chunk_size, overlap=overlap):
            chunk_index = per_source_index.get(unit.source_path, 0)
            identity = f"{unit.source_path}|{unit.page}|{chunk_index}|{text}"
            chunk_id = hashlib.sha256(identity.encode("utf-8")).hexdigest()
            chunks.append(
                Chunk(
                    id=chunk_id,
                    text=text,
                    source_path=unit.source_path,
                    source_name=unit.source_name,
                    file_type=unit.file_type,
                    page=unit.page,
                    chunk_index=chunk_index,
                    document_hash=document_hash,
                    extra_metadata=unit.metadata.copy(),
                )
            )
            per_source_index[unit.source_path] = chunk_index + 1

    return chunks
