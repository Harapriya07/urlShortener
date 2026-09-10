from app.main import encode_base62


def test_encode_base62_zero():
    assert encode_base62(0) == "0"


def test_encode_base62_small_numbers():
    assert encode_base62(1) == "1"
    assert encode_base62(10) == "a"
    assert encode_base62(61) == "Z"


def test_encode_base62_larger_numbers():
    assert encode_base62(62) == "10"
    assert encode_base62(63) == "11"
    assert encode_base62(104) == "1G"
    assert encode_base62(105) == "1H"