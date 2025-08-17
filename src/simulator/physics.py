"""
Physics placeholder module.

This module exposes a single entry point:

    simulate(mA: float, kVp: float, size: tuple[int, int] = (256, 256), seed: int | None = None) -> np.ndarray
    
Contract:
- Returns a 2D numpy array (float32) ranged in [0.0, 1.0], where 0.0 = black (high absorption), 1.0 = white.
- The GUI will map this array to an 8-bit grayscale preview.
- No side effects. Pure function given inputs.

NOTE:
- Fore V0, we intentionally return a block image to confirm wiring.
- You will replace the internals with a simple Beer Lambert style toy model in the next step.
"""
from __future__ import annotations
import numpy as np
from typing import Tuple

def simulate(mA: float, kVp: float, size: Tuple[int, int] = (256, 256), seed: int | None = None) -> np.ndarray:
    """
    Placeholder simulator. Produces a black image for now.
    
    Args:
        mA: Tube current in milliamperes.
        kVp: Tube voltage in kilovolts peak.
        size: (height, width) of the output image.
        seed: Optional RNG seed for future stochastic effects.
    
    Returns:
        np.ndarray: float32 array with shape (H, W), values in [0.0, 1.0].
    """
    h, w = map(int, size)
    img = np.zeros((h, w), dtype=np.float32)  # TODO: replace with a simple toy physics model.
    return img