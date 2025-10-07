from invenio_records_resources.services.files.extractors.base import FileExtractor


class DummyFileExtractor(FileExtractor):
    def can_process(self, file_record):
        return file_record.key.endswith(".txt")

    def list(self, file_record):
        return {"entries": [{"name": "dummy.txt", "size": "123456790"}]}

    def extract(self, file_record, path):
        class DummySendFile:
            def send_file(self):
                return f"Sending {path} from {file_record.key}"

        return DummySendFile()
