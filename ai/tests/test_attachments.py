"""Unit tests for attachment preparation."""

from __future__ import annotations

import pytest

from documents.attachments import AttachmentKind, prepare_attachment


def test_prepare_png_attachment() -> None:
    data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16
    attachment = prepare_attachment("sample.png", data, "image/png")
    assert attachment.kind is AttachmentKind.IMAGE
    assert attachment.mime_type == "image/png"
    assert attachment.data_url.startswith("data:image/png;base64,")


def test_prepare_pdf_attachment() -> None:
    data = b"%PDF-1.4 fake"
    attachment = prepare_attachment("doc.pdf", data, "application/pdf")
    assert attachment.kind is AttachmentKind.PDF


def test_reject_unsupported_type() -> None:
    with pytest.raises(ValueError, match="Unsupported"):
        prepare_attachment("notes.docx", b"abc", "application/vnd.openxmlformats")
