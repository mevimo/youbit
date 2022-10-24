"""
This file (test_util.py) contains unit tests for the util.py file.
"""
from youbit import util


def test_is_url():
    valid_url = ["https://www.google.com", "http://www.google.com", "www.google.com"]
    invalid_url = ["htt://www.google.com", "://www.google.com", "E:/foo/bar"]
    assert all(list(map(util.is_url, valid_url)))
    assert not any(list(map(util.is_url, invalid_url)))
