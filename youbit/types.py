import numpy as np
import numpy.typing as npt
from typing import Literal, Any

# Type aliases, because these complex type signatures can drastically decrease code readability
ndarr_1d_uint8 = np.ndarray[tuple[Literal[1]], np.dtype[np.uint8]]
ndarr_any = npt.NDArray[Any]