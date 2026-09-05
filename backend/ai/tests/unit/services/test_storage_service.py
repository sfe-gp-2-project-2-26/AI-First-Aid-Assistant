import pytest
import os
from first_aid_rag.services.storage_service import StorageService

def test_calculate_hash_deterministic(temp_assets_dir):
    service = StorageService(assets_dir=temp_assets_dir)
    content = b"test content"
    hash1 = service.calculate_hash(content)
    hash2 = service.calculate_hash(content)
    assert hash1 == hash2

def test_calculate_hash_different_content(temp_assets_dir):
    service = StorageService(assets_dir=temp_assets_dir)
    hash1 = service.calculate_hash(b"test content 1")
    hash2 = service.calculate_hash(b"test content 2")
    assert hash1 != hash2

def test_save_file_new(temp_assets_dir):
    service = StorageService(assets_dir=temp_assets_dir)
    file_hash, file_path, already_existed = service.save_file(b"new content")
    assert already_existed is False
    assert os.path.exists(file_path)

def test_save_file_duplicate(temp_assets_dir):
    service = StorageService(assets_dir=temp_assets_dir)
    service.save_file(b"duplicate content")
    file_hash, file_path, already_existed = service.save_file(b"duplicate content")
    assert already_existed is True

def test_exists_true(temp_assets_dir):
    service = StorageService(assets_dir=temp_assets_dir)
    file_hash, _, _ = service.save_file(b"content to check")
    assert service.exists(file_hash) is True

def test_exists_false(temp_assets_dir):
    service = StorageService(assets_dir=temp_assets_dir)
    assert service.exists("nonexistenthash") is False

