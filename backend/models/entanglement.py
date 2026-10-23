"""Werner-state entanglement swapping model."""

def werner_swap_fidelity(f1: float, f2: float) -> float:
    if not 0.25 <= f1 <= 1.0 or not 0.25 <= f2 <= 1.0:
        raise ValueError('Werner fidelity must be between 0.25 and 1.0')
    return f1 * f2 + ((1.0 - f1) * (1.0 - f2)) / 3.0


def multi_hop_fidelity(link_fidelities):
    values = list(link_fidelities)
    if not values:
        raise ValueError('At least one link is required')
    for value in values:
        if not 0.25 <= value <= 1.0:
            raise ValueError('Invalid Werner fidelity')
    result = values[0]
    for value in values[1:]:
        result = werner_swap_fidelity(result, value)
    return result
