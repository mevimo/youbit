"""
This file (test_util.py) contains unit tests for the util.py file.
"""
from youbit import util


def test_base64_encoding():
    """WHEN we use the util.dict_to_b64() and util.b64_to_dict() functions
    to encode a dictionary to a base64 string, and decode it back to a dictionary
    THEN check if the result is equal to the original input
    """
    test_dict = {"foo": "bar", "hello": "world", "integer": 6}
    b64_string = util.dict_to_b64(test_dict)
    assert isinstance(b64_string, str)
    dict_again = util.b64_to_dict(b64_string)
    assert isinstance(dict_again, dict)
    assert test_dict == dict_again


def test_is_url():
    valid_url = ["https://www.google.com", "http://www.google.com", "www.google.com"]
    invalid_url = ["htt://www.google.com", "://www.google.com", "E:/foo/bar"]
    assert all(list(map(util.is_url, valid_url)))
    assert not any(list(map(util.is_url, invalid_url)))
