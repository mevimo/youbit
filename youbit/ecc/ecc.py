"""
Provides an interface for creedsolo.pyx. Error correction is applied and removed here.
"""
from typing import Annotated

from youbit.ecc.creedsolo import RSCodec


def apply_ecc(data: bytes, ecc_symbols: Annotated[int, '0 < x < 255']) -> bytes:
    """Encodes a bytes object using reed-solomon error correction. Galois field is GF(256).
    Beware, empty bytes will be added to the input if it is not a factor of (255 - {ecc_symbols}).
    """
    if mod := len(data) % (255 - ecc_symbols):
        bytes_needed = (255 - ecc_symbols) - mod
        _add_trailing_bytes(bytes_needed)

    return RSCodec(ecc_symbols).encode(data)  # type: ignore


def _add_trailing_bytes(data: bytes, byte_count: int) -> None:
    trailing_bytes = bytearray([0] * byte_count)
    data = bytearray(data)
    data.extend(trailing_bytes)


def remove_ecc(data: bytes, ecc_symbols: Annotated[int, '0 < x < 255']) -> bytes:
    """Decodes a bytes object using reed-solomon error correction.
    Galois field is assumed to be GF(256). Input can be larger than
    the Galois Field and will be properly chunked.
    """
    return RSCodec(ecc_symbols).decode(data)[0]  # type: ignore
