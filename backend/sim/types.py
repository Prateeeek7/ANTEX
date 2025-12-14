from typing import TypedDict, Optional


class PatchParams(TypedDict):
    length_mm: float
    width_mm: float
    substrate_height_mm: float
    eps_r: float  # Dielectric constant
    feed_offset_mm: float  # Offset from center
    substrate_loss_tan: Optional[float]  # Loss tangent


class SlotParams(TypedDict):
    length_mm: float
    width_mm: float
    slot_length_mm: float
    slot_width_mm: float
    substrate_height_mm: float
    eps_r: float
    feed_offset_mm: float


class FractalParams(TypedDict):
    iterations: int
    scale_factor: float
    base_length_mm: float
    base_width_mm: float
    substrate_height_mm: float
    eps_r: float


GeometryParams = PatchParams | SlotParams | FractalParams





