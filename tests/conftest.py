"""Place for all the common fixtures"""

from fastapi import UploadFile
from app.services.vulners_service import VulnersService
from pathlib import Path

import pytest
import io
import json
import logging


@pytest.fixture(scope="session")
def service():
    """For each session"""
    return VulnersService()

@pytest.fixture(scope="session")
def sample_file_path() -> Path:
    """Get the data from the sample
        This file will be created and not commited
        gitingore is with opt/
    """
    path = Path("app/opt/data/sample.txt")
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        content = "\n".join([
            json.dumps({"name": "Django", "version": "3.2.0", "ecosystem": "PyPI"}),
            json.dumps({"name": "requests", "version": "2.25.1", "ecosystem": "PyPI"}),
        ])
        path.write_text(content)
    return path

@pytest.fixture
def upload_file_from_sample(sample_file_path):
    """Get the reference of the file"""
    content = sample_file_path.read_bytes()
    return UploadFile(filename=sample_file_path.name, file=io.BytesIO(content))


@pytest.fixture(scope="function")
def pipeline_e2e_fixture():
    """
    Dedicated fixture: sets up everything needed for end-to-end validation of file processing.
    """
    logger = logging.getLogger("tests.e2e_pipeline")
    logger.setLevel(logging.INFO)

    # if not logger.handlers:
    #     handler = logging.StreamHandler()
    #     formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
    #     handler.setFormatter(formatter)
    #     logger.addHandler(handler)

    logger.info("Starting End-to-End pipeline test setup...")

    sample_path = Path("app/opt/data/sample.txt")
    if not sample_path.exists():
        sample_path.parent.mkdir(parents=True, exist_ok=True)
        sample_path.write_text("\n".join([
            json.dumps({"name": "Django", "version": "3.2.0", "ecosystem": "PyPI"}),
            json.dumps({"name": "requests", "version": "2.25.1", "ecosystem": "PyPI"}),
        ]))
        logger.info("Sample file created at %s", sample_path.resolve())
    else:
        logger.info("Sample file found: %s", sample_path.resolve())

    content = sample_path.read_bytes()
    upload_file = UploadFile(filename=sample_path.name, file=io.BytesIO(content))
    service = VulnersService()

    logger.info("End-to-end pipeline fixture ready.")

    yield service, upload_file

    logger.info("End-to-end pipeline teardown complete.")
