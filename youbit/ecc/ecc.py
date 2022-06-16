from youbit.ecc.creedsolo import RSCodec


def ecc_encode(data: bytes, symbols: int = 32) -> bytes:
    """Encodes a bytes object using reed-solomon error correction.
    Galois field is GF(256). Input can be larger than the Galois Field
    and will be properly chunked.

    :param data: The data that needs to be encoded.
    :type data: bytes
    :param symbols: How many ecc symbols to use, defaults to 16
    :type symbols: int, optional
    :return: The encoded data
    :rtype: bytes
    """
    if not 0 < symbols < 255:
        raise ValueError(f'Invalid symbols argument: {symbols}. Must be between 0 and 255 exclusive.') 
    return RSCodec(symbols).encode(data)  # type: ignore


def ecc_decode(data: bytes, symbols: int) -> bytes:
    """Decodes a bytes object using reed-solomon error correction.
    Galois field is assumed to be GF(256). Input can be larger than
    the Galois Field and will be proeprly chunked.

    :param data: The data that needs to be decoded
    :type data: bytes
    :param symbols: How many ecc symbols were used during encoding
    :type symbols: int
    :return: The decoded data
    :rtype: bytes
    """
    if not 0 < symbols < 255:
        raise ValueError(f'Invalid symbols argument: {symbols}. Must be between 0 and 255 exclusive.') 
    return RSCodec(symbols).decode(data)[0]  # type: ignore
