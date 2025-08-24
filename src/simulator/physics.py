"""
Beer-Lumbert toy model (simple, single-material phantom).

I(x, y) = I0 * exp(-mu(kVp) * t(x,y))

- I0 (incident intensity) increases with mA (exposure-like gain).
- mu (effective linear attention, [1/cm]) decreases with kVp (harder beam).
- t(x,y) is the object thickness [cm] along the beam at each pixel.

Phantom:
- A solid sphere (actually, a 3D sphere intersected by X-ray paths) centered in the FOV.
- Thickness map: t(r) = 2 * sqrt(R^2 - r^2) for r <= R, else 0, where r is radial distance in cm.

This is a *didactic* model:
- Single material, energy dependence via a simple power law in kVp.
- No scatter, heel effect, detector MTF/NRF, or noise (to be added later).
"""
from __future__ import annotations
from typing import Tuple, Optional
import numpy as np

# ------------------------------------------
# Tunable "physics" constants
# ------------------------------------------
FOV_X_CM = 20.0
SPHERE_RADIUS_CM = 6.0
SPHERE_CENTER_CM = (0.0, 0.0)

# Effective linear attenuation (very rough; pedagogical)
MU_REF_CM1 = 0.50
KVP_REF = 60.0
MU_POWER = 2.2
MU_MIN = 0.05

# Incident intensity scaling from mA
I0_MIN = 0.60
I0_MAX = 1.40

def _normalize(v: float, lo: float, hi: float) -> float:
    """
    Clamp-linear normalize v into [0,1] for [lo,hi].
    """
    if hi <= lo:
        return 0.0
    return float(np.clip((v - lo) / (hi - lo), 0.0, 1.0))

def _sphere_thickness_map(size: Tuple[int, int],
                          fov_x_cm: float,
                          radius_cm: float,
                          center_cm: Tuple[float, float] = (0.0, 0.0)) -> np.ndarray:
    """
    Build thickness map t(x,y) [cm] for a solid sphere of radius R [cm] centered at (cx,cy) [cm].
    Coordinate system: x to the right, y down; origin at image center.
    
    FOV is defined along X: width = fov_x_cm.
    Pixel size [cm/px] = fov_x_cm / W. Y-range is derived to keep square pixels.
    """
    H, W = int(size[0]), int(size[1])
    assert H > 0 and W > 0

    px_cm = fov_x_cm / float(W)
    fov_y_cm = px_cm * H

    # Build physical coordinate grid (centered)
    x = (np.linspace(0, W - 1, W, dtype=np.float32) - (W - 1) / 2.0) * px_cm
    y = (np.linspace(0, H - 1, H, dtype=np.float32) - (H - 1) / 2.0) * px_cm
    yy, xx = np.meshgrid(y, x, indexing="ij")

    # Shift by sphere center (cx, cy)
    cx, cy = center_cm
    dx = xx -cx
    dy = yy - cy
    r = np.sqrt(dx**2 + dy**2)

    # Thickness through a sphere at radial distance r: 2 * sqrt(R^2 - r^2), else 0
    R = float(radius_cm)
    inside = r <= R
    t = np.zeros((H, W), dtype=np.float32)
    # Avoid negative due to float roundoff
    t[inside] = 2.0 * np.sqrt(np.maximum(0.0, R**2 - r[inside]**2)).astype(np.float32)
    return t # [cm]

def simulate(mA: float, 
             kVp: float, 
             size: Tuple[int, int] = (256, 256), 
             seed: Optional[int] = None) -> np.ndarray:
    """
    Compute a Beer-Lambert projection of a single material spherical phantom.
    
    Args:
        mA: Tube current [mA], e.g., 10..500. Controls incident intensity I0.
        kVp: Tube voltage [kVp], e.g., 40..120. Controls effective mu (attenuation).
        size: (H, W) of the output array.
        seed: Unused here (reserved for future stochastic effects).
    
    Returns:
        float32 image (H, W) in [0, 1], where 0=black (strong absorption), 1=white (air-like).
    """
    H, W = int(size[0]), int(size[1])

    # 1) Thickness map [cm]
    t_cm = _sphere_thickness_map(size=(H, W),
                                 fov_x_cm=FOV_X_CM,
                                 radius_cm=SPHERE_RADIUS_CM,
                                 center_cm=SPHERE_CENTER_CM)  # [cm]
    
    # 2) Effective attenuation mu(kVp) [1/cm] (simple power-law falloff with energy)
    kVp_eff = float(max(10.0, kVp)) # guard against zero/neq
    mu = MU_REF_CM1 * (KVP_REF / kVp_eff) ** MU_POWER
    mu = float(max(MU_MIN, mu))  # floor to avoid vanish

    # 3) Incident intensity I0 from mA (linear ramp)
    n_mA = _normalize(mA, 10.0, 500.0)
    I0 = I0_MIN + (I0_MAX - I0_MIN) * n_mA

    # 4) Beer-Lambert: I = I0 * exp(-mu * t)
    I = I0 * np.exp(-mu * t_cm, dtype=np.float32)

    # 5) Display clamp to [0,1]
    I = np.clip(I, 0.0, 1.0).astype(np.float32)
    return I