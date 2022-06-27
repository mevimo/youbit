"""
Provides a small interface between creedsolo.pyx and the rest of YouBit.
"""
from youbit.ecc.creedsolo import RSCodec


def ecc_encode(data: bytes, ecc_symbols: int = 32) -> bytes:
    """Encodes a bytes object using reed-solomon error correction.
    Galois field is GF(256). Input can be larger than the Galois Field
    and will be properly chunked.

    Beware, if the length of {data} is not a factor of (255 - {ecc_symbols}),
    zero's will be added until it is.

    :param data: The data that needs to be encoded.
    :type data: bytes
    :param symbols: How many ecc symbols to use, defaults to 32
    :type symbols: int, optional
    :return: The encoded data
    :rtype: bytes
    """
    if not 0 < ecc_symbols < 255:
        raise ValueError(
            f"Invalid symbols argument: {ecc_symbols}. Must be between 0 and 255 exclusive."
        )
    if mod := len(data) % (255 - ecc_symbols):
        padding_count = (255 - ecc_symbols) - mod
        padding = bytearray([0] * padding_count)
        data = bytearray(data)
        data.extend(padding)
        # Let's say our {data} is not a factor of 255. If we divide it by 255,
        # we get a remainder of 69. The reed-solomon codec does not care, it
        # simply encodes the last 69-bytes long message like any other. Let's
        # say we used an {ecc} value of 32: the last message will simply be
        # (69+32) = 101 bytes long instead of 255. The reed-solomon -decoder-
        # will process this message by message, and when it reaches the last,
        # smaller message, it will not care either. It interprets the last 32
        # bytes as the ecc symbols, the other 69 as data symbols, and is able
        # to decode the message just fine.
        # BUT if we were to add any trailing null bytes to this message (like
        # we do when we add black pixels to fill out the last frame), then our
        # last message of length 101 will be flooded with null bytes. If even 1
        # null bytes is added, the decoding process will fail, because our
        # reed-solomon decoder will still assume the last 32 bytes to be ecc
        # symbols, but one of them is not. The last message would be corrupt.
        # And that is why we ensure every message passed to the encoder is a
        # factor of 255.
    return RSCodec(ecc_symbols).encode(data)  # type: ignore


def ecc_decode(data: bytes, symbols: int) -> bytes:
    """Decodes a bytes object using reed-solomon error correction.
    Galois field is assumed to be GF(256). Input can be larger than
    the Galois Field and will be properly chunked.

    :param data: The data that needs to be decoded
    :type data: bytes
    :param symbols: How many ecc symbols were used during encoding
    :type symbols: int
    :return: The decoded data
    :rtype: bytes
    """
    if not 0 < symbols < 255:
        raise ValueError(
            f"Invalid symbols argument: {symbols}. Must be between 0 and 255 exclusive."
        )
    return RSCodec(symbols).decode(data)[0]  # type: ignore
