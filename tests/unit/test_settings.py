"""
This file (test_encode.py) contains unit tests for the settings.py file.
"""
import pytest

from youbit.settings import Settings, Resolution, BitsPerPixel, Browser


def test_settings_creation():
    settings = Settings()
    assert settings

def test_settings_creation_failure():
    with pytest.raises(TypeError):
        Settings("Should not accept arguments")

def test_setters_valid_settings():
    settings = Settings()

    settings.resolution = Resolution.HD
    settings.bits_per_pixel = BitsPerPixel.ONE
    settings.ecc_symbols = 100
    settings.constant_rate_factor = 25
    settings.null_frames = True
    settings.browser = Browser.CHROME

def test_setters_invalid_settings():
    settings = Settings()

    with pytest.raises(ValueError):
        settings.resolution = "Should be Resolution object"
    with pytest.raises(ValueError):
        settings.bits_per_pixel = "Should be BitsPerPixel object"
    with pytest.raises(ValueError):
        settings.ecc_symbols = 999
    with pytest.raises(ValueError):
        settings.constant_rate_factor = 999
    with pytest.raises(ValueError):
        settings.null_frames = "Should be boolean"
    with pytest.raises(ValueError):
        settings.browser = "Should be Browser object"
