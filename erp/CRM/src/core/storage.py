"""Filesystem storage helpers for uploaded CRM files."""

from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
from uuid import uuid4

from core.config import get_settings
from core.exceptions import InvalidOperationError, NotFoundError

UPLOAD_CHUNK_SIZE = 1024 * 1024
ALLOWED_EXTENSIONS: set[str] = {".pdf", ".jpg", ".jpeg", ".png"}
MAX_UPLOAD_SIZE_BYTES = 20 * 1024 * 1024

ALLOWED_DOCUMENT_MIME_TYPES: frozenset[str] = frozenset(
    {
        "application/pdf",
        "image/jpeg",
        "image/png",
        "image/tiff",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "text/plain",
        "text/csv",
    }
)


class UploadFileLike(Protocol):
    """Minimal async upload file protocol used by document services."""

    filename: str | None
    content_type: str | None

    async def read(self, size: int = -1) -> bytes:
        """Read bytes from the uploaded file."""


@dataclass(frozen=True)
class StoredUpload:
    """Metadata for a file saved to local storage."""

    stored_path: str
    original_filename: str
    content_type: str | None
    size_bytes: int


def _storage_root(storage_root: str | Path | None = None) -> Path:
    root = storage_root or get_settings().document_storage_path
    return Path(root)


def _stored_filename(original_filename: str) -> str:
    suffix = Path(original_filename).suffix
    if len(suffix) > 20:
        suffix = ""
    return f"{uuid4().hex}{suffix.lower()}"


async def save_upload(
    upload: UploadFileLike,
    *,
    directory_parts: tuple[str, ...],
    storage_root: str | Path | None = None,
    allowed_mime_types: frozenset[str] | None = None,
) -> StoredUpload:
    """Persist an uploaded file and return metadata for database storage.

    Validates file type (PDF/JPG/PNG) and size (max 20 MiB).
    Optional ``allowed_mime_types`` restricts acceptable content types.
    """

    if allowed_mime_types and upload.content_type and upload.content_type not in allowed_mime_types:
        raise InvalidOperationError(
            f"File type '{upload.content_type}' is not allowed. "
            f"Accepted types: {', '.join(sorted(allowed_mime_types))}",
        )

    original_filename = Path(upload.filename or "upload").name or "upload"
    suffix = Path(original_filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise InvalidOperationError(
            "Invalid file type. Only PDF, JPG, and PNG files are allowed",
            details={"filename": original_filename, "suffix": suffix},
        )

    directory = _storage_root(storage_root).joinpath(*directory_parts)
    directory.mkdir(parents=True, exist_ok=True)
    stored_path = directory / _stored_filename(original_filename)

    size_bytes = 0
    try:
        with stored_path.open("wb") as output:
            while chunk := await upload.read(UPLOAD_CHUNK_SIZE):
                size_bytes += len(chunk)
                if size_bytes > MAX_UPLOAD_SIZE_BYTES:
                    raise InvalidOperationError(
                        "File exceeds maximum upload size of 20 MiB",
                        details={
                            "max_bytes": MAX_UPLOAD_SIZE_BYTES,
                            "uploaded_bytes": size_bytes,
                        },
                    )
                output.write(chunk)
        if size_bytes == 0:
            raise InvalidOperationError("Uploaded file cannot be empty")
    except Exception:
        delete_stored_file(str(stored_path))
        raise

    return StoredUpload(
        stored_path=str(stored_path),
        original_filename=original_filename,
        content_type=upload.content_type,
        size_bytes=size_bytes,
    )


def delete_stored_file(stored_path: str) -> None:
    """Delete a stored file if it still exists."""

    with suppress(FileNotFoundError):
        Path(stored_path).unlink()


def stored_file_path(stored_path: str) -> Path:
    """Return an uploaded file path or raise if the blob is missing."""

    path = Path(stored_path)
    if not path.is_file():
        raise NotFoundError("Uploaded file not found", details={"path": stored_path})
    return path
