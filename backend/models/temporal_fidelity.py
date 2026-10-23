"""Temporal fidelity models for quantum-network simulation."""

from __future__ import annotations

import math


def predict_memory_fidelity(
    initial_fidelity: float,
    storage_time: float,
    decoherence_rate: float,
) -> float:
    """Predict fidelity under a simplified depolarizing-memory model."""

    if not 0.0 <= initial_fidelity <= 1.0:
        raise ValueError("initial_fidelity must be between 0 and 1")

    if storage_time < 0.0:
        raise ValueError("storage_time must be non-negative")

    if decoherence_rate < 0.0:
        raise ValueError("decoherence_rate must be non-negative")

    return (
        0.25
        + (initial_fidelity - 0.25)
        * math.exp(-decoherence_rate * storage_time)
    )


def calculate_aoi(
    current_time: float,
    measurement_time: float,
) -> float:
    """Calculate controller Age of Information."""

    if not math.isfinite(current_time):
        raise ValueError("current_time must be finite")

    if not math.isfinite(measurement_time):
        raise ValueError("measurement_time must be finite")

    age = current_time - measurement_time

    if age < 0.0:
        raise ValueError(
            "measurement_time cannot exceed current_time"
        )

    return age
