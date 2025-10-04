"""
Tests for validation and processing pipeline in VulnersService.
Test case for -  _read_file, _validate_file_content,
                _build_payload, _validate_and_process_file
"""

from fastapi import HTTPException
from http import HTTPStatus
from app.config import Config

import pytest
import io

@pytest.mark.positive
@pytest.mark.file
def test_read_file_valid(service, upload_file_from_sample):
    """Test to make sure of file connect correct and 
    stripped correctly.
    """
    content = service._read_file(upload_file_from_sample)

    assert "Django" in content
    assert "requests" in content
    assert not content.endswith("\n")

@pytest.mark.negative
@pytest.mark.file
def test_read_file_empty(service):
    """Test to make sure if file content is empty
        then thru Exception
    """
    from fastapi import UploadFile
    empty_file = UploadFile(filename="empty.txt", file=io.BytesIO(b""))
    with pytest.raises(HTTPException) as exc:
        service._read_file(empty_file)

    assert exc.value.status_code == HTTPStatus.BAD_REQUEST
    assert "empty" in exc.value.detail.lower()

@pytest.mark.positive
@pytest.mark.file
def test_validate_file_content_valid(service, sample_file_path):
    """Test to make sure of the content retrieved
        is a well formed JSON
    """
    content = sample_file_path.read_text()
    rows = service._validate_file_content(content, Config.EXPECTED_KEYS)
    
    assert isinstance(rows, list)
    assert all(all(k in row for k in Config.EXPECTED_KEYS) for row in rows)
    assert rows[0]["ecosystem"] == "PyPI"

@pytest.mark.negative
@pytest.mark.file
@pytest.mark.parametrize("bad_line", [
    '{"name": "Django", "version": "3.2.0"',          # malformed JSON
    '{"name": "Flask"}',                              # missing fields
])
def test_validate_file_content_invalid(service, bad_line):
    """Test to validate row wise from content (bad_line)
        Should through an error HTTPException"""
    with pytest.raises(HTTPException) as exc:
        service._validate_file_content(bad_line, Config.EXPECTED_KEYS)
    assert exc.value.status_code == HTTPStatus.BAD_REQUEST

@pytest.mark.positive
def test_build_payload_valid(service):
    """Test to validate the created payload
    """
    rows = [
        {"name": "Flask", "version": "2.0.0", "ecosystem": "PyPI"},
        {"name": "FastAPI", "version": "0.95.0", "ecosystem": "PyPI"},
    ]
    payload, names = service._build_payload(rows, Config.EXPECTED_KEYS)
    assert "queries" in payload
    assert payload["queries"][0]["package"]["name"] == "Flask"
    assert names == ["Flask", "FastAPI"]

@pytest.mark.pipeline
def test_validate_and_process_file_pipeline(service, upload_file_from_sample):
    """Test to validate end to end of 
        UploadFile → payload + names.
    """
    payload, names = service._validate_and_process_file(upload_file_from_sample)

    # Structure checks
    assert isinstance(payload, dict)
    assert "queries" in payload
    assert isinstance(names, list)
    assert all(isinstance(n, str) for n in names)
    assert len(payload["queries"]) == len(names)

    # Content checks
    first_query = payload["queries"][0]
    assert "version" in first_query
    assert "package" in first_query
    assert first_query["package"]["ecosystem"] == "PyPI"


# @pytest.mark.positive
# def test_validate_and_process_file_pipeline(pipeline_e2e_fixture):
#     """End-to-end validation pipeline using sample.txt file."""
#     service, upload_file = pipeline_e2e_fixture

#     payload, names = service._validate_and_process_file(upload_file)
#     assert isinstance(payload, dict)
#     assert "queries" in payload
#     assert names is not None
