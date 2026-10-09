from __future__ import annotations

import unittest

from rag.chunking import chunk_units, split_text
from rag.loaders import TextUnit, clean_text


class CleanTextTests(unittest.TestCase):
    def test_normalizes_spaces_and_blank_lines(self) -> None:
        raw = "  Dòng một   có khoảng trắng.\r\n\r\n\r\n  Dòng hai.  "
        self.assertEqual(clean_text(raw), "Dòng một có khoảng trắng.\n\nDòng hai.")

    def test_repairs_line_break_hyphen(self) -> None:
        self.assertEqual(clean_text("thông-\ntin"), "thôngtin")


class ChunkingTests(unittest.TestCase):
    def test_chunks_respect_size_and_overlap(self) -> None:
        text = " ".join(f"Câu số {index} có nội dung kiểm thử." for index in range(80))
        chunks = split_text(text, chunk_size=220, overlap=40)
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(1 <= len(chunk) <= 220 for chunk in chunks))

    def test_chunk_ids_are_deterministic(self) -> None:
        unit = TextUnit("demo/a.txt", "a.txt", "txt", "Nội dung mẫu.", 0)
        first = chunk_units([unit])
        second = chunk_units([unit])
        self.assertEqual(first[0].id, second[0].id)
        self.assertEqual(first[0].metadata()["source_path"], "demo/a.txt")

    def test_invalid_overlap_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            split_text("Nội dung", chunk_size=100, overlap=100)


if __name__ == "__main__":
    unittest.main()
