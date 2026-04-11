from __future__ import annotations
import numpy as np
from .base import BaseStep


class DownsampleStep(BaseStep):
    """Density-normalized downsampling.

    Cells in dense regions are sampled with lower probability so that
    rare populations (low density) are preserved after downsampling.

    Inclusion probability for cell i: ``p_i = min(1, target_count * w_i / sum(w))``
    where ``w_i = 1 / density_i``.
    """

    def __init__(self, downsample_target: float = 0.05, random_state: int | None = None) -> None:
        if not 0 < downsample_target <= 1:
            raise ValueError(f"downsample_target must be in (0, 1], got {downsample_target}")
        self.downsample_target = downsample_target
        self.random_state = random_state

    def run(self, data: np.ndarray, *, density: np.ndarray, **ctx) -> dict:
        rng = np.random.default_rng(self.random_state)
        n = len(data)
        target_count = max(1, int(n * self.downsample_target))

        weights = 1.0 / density
        probs = np.minimum(1.0, target_count * weights / weights.sum())

        mask = rng.random(n) < probs
        down_idx = np.where(mask)[0]
        return {"X_down": data[down_idx], "down_idx": down_idx}
