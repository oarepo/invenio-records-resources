import os
from typing import Protocol

from invenio_records_resources.records.api import FileRecord


class SendFileProtocol(Protocol):
    def send_file(self) -> None: ...


class FileExtractor:
    @staticmethod
    def file_extension(file_record):
        """Determine if the key has a specific extension."""
        return os.path.splitext(file_record.key)[-1].lower()

    def can_process(self, file_record: FileRecord) -> bool:
        """Determine if this extractor can process a given file record."""

    def list(self, file_record: FileRecord) -> list[dict]:
        """Return a listing of the file."""

    def extract(self, file_record: FileRecord, path: str) -> SendFileProtocol:
        """Extract a specific file or directory from the file record."""
