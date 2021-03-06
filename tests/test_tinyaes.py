import pytest
from pytest import fixture
from hypothesis import given, example
from hypothesis.strategies import binary

import tinyaes


@fixture
def aes_enc():
    return tinyaes.AES(b'0123456789ABCDEF',
                       b'1234567890ABCDEF')


@fixture
def aes_dec():
    # Need to have two same-keys instancies
    return tinyaes.AES(b'0123456789ABCDEF',
                       b'1234567890ABCDEF')


@fixture
def aes_dec2():
    # Different key for decoding test
    return tinyaes.AES(b'ABCDEF0123456789',
                       b'ABCDEF1234567890')


@fixture
def aes_dec3():
    # Different key for decoding test
    return tinyaes.AES(b'56789ABCDEF01234',
                       b'567890ABCDEF1234')


@given(key=binary(min_size=16, max_size=16))
def test_keys_of_len_16_are_ok(key, aes_enc):
    tinyaes.AES(key)


@given(key=binary())
def test_keys_of_len_not_16_are_raise(key, aes_enc):
    if len(key) != 16:
        with pytest.raises(ValueError):
            tinyaes.AES(key)


@given(iv=binary(min_size=16, max_size=16))
@example(iv=None)
def test_ivs_of_len_16_or_None_are_ok(iv, aes_enc):
    tinyaes.AES(b'0'*16, iv)


@given(iv=binary())
def test_ivs_of_len_not_16_are_raise(iv, aes_enc):
    if len(iv) != 16:
        with pytest.raises(ValueError):
            tinyaes.AES(b'0'*16, iv)


@given(data=binary())
def test_decode_inverts_encode(data, aes_enc, aes_dec):
    encoded = aes_enc.CTR_xcrypt_buffer(data)
    assert aes_dec.CTR_xcrypt_buffer(encoded) == data


@given(data=binary(min_size=2))
@example(data=b'AAHTAWcEngYpAz0BpgNBBdACdgPDBjgEAQWHAA==')
def test_encode_leaves_data_unmodified(data, aes_enc):
    original_data = data[:len(data)//2] + data[len(data)//2:]  # Force a copy not allowing any sharing
    assert len(original_data) == len(data)
    assert original_data == data
    assert original_data is not data
    aes_enc.CTR_xcrypt_buffer(data)
    assert len(original_data) == len(data)
    assert original_data == data
    assert original_data is not data


@given(data=binary(min_size=2, max_size=100))
def test_different_keys_do_not_decode(data, aes_enc, aes_dec2, aes_dec3):
    # - the empty buffer is encoded as an empty buffer,
    #   so the test is known to fail
    # - small buffers suffers some collision probability
    encoded = aes_enc.CTR_xcrypt_buffer(data)
    # we can expect a single collision, but not two with two different keys and ivs
    assert aes_dec2.CTR_xcrypt_buffer(encoded) != data \
        or aes_dec3.CTR_xcrypt_buffer(encoded) != data
