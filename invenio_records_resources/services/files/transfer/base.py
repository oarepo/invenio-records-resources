# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
# Copyright (C) 2025 CESNET.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
"""Base transfer class."""

from abc import ABC

from flask_babel import lazy_gettext as _
from fs.errors import CreateFailed
from invenio_files_rest.errors import FileSizeError
from werkzeug.exceptions import ClientDisconnected

from invenio_records_resources.records.api import Record
from invenio_records_resources.services.errors import TransferException
from invenio_records_resources.services.files.service import FileService

from ..schema import BaseTransferSchema


class TransferStatus:
    """Transfer status. Constants to be used as return values for get_status."""

    #  Can not be enum to be json serializable, so just a class with constants.

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class Transfer(ABC):
    """Local transfer."""

    transfer_type: str
    """
    The transfer type for this transfer instance.
    Overriding classes must set this class attribute.
    """

    Schema = BaseTransferSchema
    """
    Schema definition for transfer metadata. Transfer providers are free to supply
    their own schema with additional fields.
    """

    def __init__(
        self,
        record: Record,
        key: str,
        file_service: FileService,
        uow=None,
    ):
        """Constructor."""
        self.record = record
        self.key = key
        self.file_service = file_service
        self.uow = uow

    def init_file(self, record, file_metadata):
        """Initialize a file and return a file record."""

        # do not modify the original metadata as other file service components
        # might need it
        metadata = {**file_metadata}
        return record.files.create(
            key=metadata.pop("key"),
            transfer=metadata.pop("transfer"),
            data=metadata,
        )

    @property
    def file_record(self):
        """Get the file record."""
        return self.record.files[self.key]

    def set_file_content(self, stream, content_length):
        """Set file content."""
        bucket = self.record.bucket

        size_limit = bucket.size_limit
        if content_length and size_limit and content_length > size_limit:
            desc = (
                _("File size limit exceeded.")
                if isinstance(size_limit, int)
                else size_limit.reason
            )
            raise FileSizeError(description=desc)

        try:
            self.record.files.create_obj(
                self.file_record.key, stream, size=content_length, size_limit=size_limit
            )
        except (ClientDisconnected, CreateFailed):
            raise TransferException(
                f'Transfer of File with key "{self.file_record.key}" failed.'
            )

    def commit_file(self):
        """Commit a file."""
        # fetch files can be committed, its up to permissions to decide by who
        # e.g. system, since its the one downloading the file
        self.record.files.commit(self.file_record.key)

    def delete_file(self):
        """
        Delete a file.

        This method is called before a file is removed from the record.
        It can be used, for example, to do a cleanup of the file in the storage.
        """

    @property
    def status(self):
        """
        Get status of the upload of the passed file record.

        Returns TransferStatus.COMPLETED if the file is uploaded,
        TransferStatus.PENDING if the file is not uploaded yet or
        TransferStatus.FAILED if the file upload failed.
        """
        if self.file_record is not None and self.file_record.file is not None:
            return TransferStatus.COMPLETED

        return TransferStatus.PENDING

    def expand_links(self, identity, self_url):
        """Expand links."""
        return {}

    def send_file(self, *, restricted, as_attachment):
        """Send file to the client."""
        return self.file_record.object_version.send_file(
            restricted=restricted, as_attachment=as_attachment
        )
