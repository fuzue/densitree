from __future__ import annotations
from abc import ABC, abstractmethod
import numpy as np


class BaseStep(ABC):
    """Abstract base for all SPADE pipeline steps.

    Each step receives the shared pipeline context as keyword arguments
    and returns a dict of new keys to merge into that context.
    """

    @abstractmethod
    def run(self, data: np.ndarray, **ctx) -> dict:
        """Run this step.

        Parameters
        ----------
        data:
            The (possibly transformed) input array, shape (n_cells, n_features).
        **ctx:
            Accumulated outputs from previous steps.

        Returns
        -------
        dict
            New context keys produced by this step.
        """
        ...
