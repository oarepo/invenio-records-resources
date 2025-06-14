# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2023 CERN.
# Copyright (C) 2020 Northwestern University.
# Copyright (C) 2025 CESNET.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

import pytest
from flask_principal import Identity, Need, UserNeed
from invenio_app.factory import create_api as _create_api

from invenio_records_resources.services import FileService, RecordService
from tests.mock_module.config import FileServiceConfig, ServiceConfig

pytest_plugins = ("celery.contrib.pytest",)


@pytest.fixture(scope="module")
def app_config(app_config):
    """Override pytest-invenio app_config fixture.

    Needed to set the fields on the custom fields schema.
    """
    app_config["RECORDS_RESOURCES_FILES_ALLOWED_DOMAINS"] = [
        "inveniordm.test",
    ]
    app_config["RECORDS_RESOURCES_FILES_ALLOWED_REMOTE_DOMAINS"] = [
        "inveniordm.test",
    ]
    app_config["FILES_REST_STORAGE_CLASS_LIST"] = {
        "L": "Local",
        "F": "Fetch",
        "R": "Remote",
    }

    app_config["FILES_REST_DEFAULT_STORAGE_CLASS"] = "L"

    app_config["RECORDS_REFRESOLVER_CLS"] = (
        "invenio_records.resolver.InvenioRefResolver"
    )
    app_config["RECORDS_REFRESOLVER_STORE"] = (
        "invenio_jsonschemas.proxies.current_refresolver_store"
    )

    # for http Range testing
    app_config["FILES_REST_ALLOW_RANGE_REQUESTS"] = True

    app_config["THEME_FRONTPAGE"] = False

    return app_config


@pytest.fixture(scope="module")
def extra_entry_points():
    """Extra entry points to load the mock_module features."""
    return {
        "invenio_db.model": [
            "mock_module = tests.mock_module.models",
        ],
        "invenio_jsonschemas.schemas": [
            "mock_module = tests.mock_module.jsonschemas",
        ],
        "invenio_search.mappings": [
            "records = tests.mock_module.mappings",
        ],
        "invenio_base.api_blueprints": [
            "mock_module_mocks = tests.mock_module:create_mocks_bp",
            # still present even though above doesn't support files
            "mock_module_mocks_files = tests.mock_module:create_mocks_files_bp",
        ],
    }


@pytest.fixture(scope="module")
def create_app(instance_path, entry_points):
    """Application factory fixture."""
    return _create_api


@pytest.fixture(scope="module")
def file_service():
    """File service shared fixture."""
    return FileService(FileServiceConfig)


@pytest.fixture(scope="module")
def service(appctx):
    """Service instance."""
    return RecordService(ServiceConfig)


@pytest.fixture(scope="function")
def input_data():
    """Input data (as coming from the view layer)."""
    return {
        "metadata": {"title": "Test", "type": {"type": "test"}},
    }


@pytest.fixture(scope="module")
def identity_simple():
    """Simple identity fixture."""
    i = Identity(1)
    i.provides.add(UserNeed(1))
    i.provides.add(Need(method="system_role", value="any_user"))
    i.provides.add(Need(method="system_role", value="authenticated_user"))
    return i
