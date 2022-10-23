import pytest
from importlib.metadata import version

from youbit import Metadata
from youbit.settings import Settings


C_VALID_BASE64_METADATA = "gASVZQEAAAAAAACMD3lvdWJpdC5tZXRhZGF0YZSMCE1ldGFkYXRhlJOUKYGUfZQojAhmaWxlbmFtZZSMEnlvdWJpdC1leGFtcGxlLmpwZ5SMCG1kNV9oYXNolIwgMjdjYTM5MWEzODJjYzAyODdhYmQzMTc5MDQwNTcxMjWUjAlfc2V0dGluZ3OUjA95b3ViaXQuc2V0dGluZ3OUjAhTZXR0aW5nc5STlCmBlH2UKIwLX3Jlc29sdXRpb26UaAqMClJlc29sdXRpb26Uk5RNgAdNOASGlIWUUpSMD19iaXRzX3Blcl9waXhlbJRoCowMQml0c1BlclBpeGVslJOUSwGFlFKUjAxfZWNjX3N5bWJvbHOUSyCMFV9jb25zdGFudF9yYXRlX2ZhY3RvcpRLEowMX251bGxfZnJhbWVzlImMCF9icm93c2VylE51YowOeW91Yml0X3ZlcnNpb26UjAtwcmVoaXN0b3JpY5R1Yi4="


def test_metadata_creation_success() -> None:
    valid_test_settings = Settings()
    metadata = Metadata()
    metadata.settings = valid_test_settings
    metadata.filename = "This is valid"
    metadata.md5_hash = "This is valid"
    assert metadata.youbit_version == version("youbit")


def test_metadata_creation_fail() -> None:
    metadata = Metadata()
    with pytest.raises(ValueError):
        metadata.settings = "Not a Settings object - invalid!"


def test_metadata_export() -> None:
    metadata = Metadata(
        filename = "test",
        md5_hash = "test",
        settings = Settings()
    )
    export_str = metadata.export_as_base64()
    assert export_str
    assert isinstance(export_str, str)


def test_metadata_import() -> None:
    metadata = Metadata.create_from_base64(C_VALID_BASE64_METADATA)
    assert isinstance(metadata, Metadata)
    assert isinstance(metadata.settings, Settings)


def test_eq_true() -> None:
    metadata1, metadata2 = Metadata(), Metadata()
    metadata1.filename = "unittest"
    metadata2.filename = "unittest"
    assert metadata1 == metadata2


def test_eq_false() -> None:
    metadata1, metadata2 = Metadata(), Metadata()
    metadata2.filename = "unittest"
    assert not metadata1 == metadata2


def test_metadata_roundtrip() -> None:
    metadata = Metadata(settings=Settings())
    metadata.filename = "unittest"
    export_str = metadata.export_as_base64()

    metadata2 = Metadata.create_from_base64(export_str)
    assert metadata == metadata2