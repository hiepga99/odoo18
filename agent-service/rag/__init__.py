"""Pipeline RAG tiếng Việt cho tài liệu nội bộ doanh nghiệp."""

import sys


def _configure_utf8_console() -> None:
    """Tránh lỗi UnicodeEncodeError trên PowerShell dùng code page cũ."""

    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (AttributeError, ValueError):
                pass


_configure_utf8_console()

__version__ = "0.1.0"
