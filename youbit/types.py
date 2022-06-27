from typing import Literal, Any, Tuple

import numpy as np
import numpy.typing as npt


# Gotta stay DRY eh
ndarr_1d_uint8 = np.ndarray[Tuple[Literal[1]], np.dtype[np.uint8]]
ndarr_any = npt.NDArray[Any]
