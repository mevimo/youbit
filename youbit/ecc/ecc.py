"""
Provides an interface for creedsolo.pyx. Error correction is applied and removed here.
"""
from typing import Annotated
from typing import Union

from youbit.ecc.creedsolo import RSCodec


def apply_ecc(data: Union[bytes, bytearray], ecc_symbols: Annotated[int, '0 < x < 255']) -> bytearray:
    """Encodes a bytes object using reed-solomon error correction. Galois field is GF(256).
    BEWARE: nulls (zeros) can be added if the input is not a factor of
    (255 - {ecc_symbols})!
    This is only acceptable at the very end of a file.
    """
    if mod := len(data) % (255 - ecc_symbols):
        bytes_needed = (255 - ecc_symbols) - mod
        data = _add_trailing_bytes(data, bytes_needed)

    return RSCodec(ecc_symbols).encode(data)  # type: ignore


def _add_trailing_bytes(data: Union[bytes, bytearray], byte_count: int) -> bytearray:
    data_bytearray = bytearray(data)
    trailing_bytes = bytearray([0] * byte_count)
    data_bytearray.extend(trailing_bytes)
    return data_bytearray


def remove_ecc(data: Union[bytes, bytearray], ecc_symbols_used: Annotated[int, '0 < x < 255']) -> bytearray:
    """Removes error correction from bytes object.
    BEWARE: if processing data in chunks, only pass data with a length
    that is a factor of 255, with the exception of the very last chunk!
    """        
    return RSCodec(ecc_symbols_used).decode(data)[0]  # type: ignore
