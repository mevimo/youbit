from youbit.ecc.ecc import apply_ecc, remove_ecc
from youbit.types import ndarr_1d_uint8


def test_add_trailing_bytes() -> None:
    arr = bytearray([0] * 269)
    new_arr = apply_ecc(arr, ecc_symbols=31)
    assert len(new_arr) == 510


def test_ecc(test_arr: ndarr_1d_uint8) -> None:
    arr = test_arr.tobytes()
    ecc_arr = apply_ecc(arr, ecc_symbols=20)
    assert arr != ecc_arr
    assert len(ecc_arr) > len(arr)

    back_again_arr = remove_ecc(ecc_arr, 20)
    assert arr == back_again_arr[:-40]  # 40 zeros should have been appended
