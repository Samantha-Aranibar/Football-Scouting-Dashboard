# Weights per position group. Each group's weights add up to 1.
# The keys are the same metric names we used for the percentiles in 02_eda.ipynb

WEIGHTS = {
    "Midfielder": {
        "pass_accuracy_pct": 0.25,
        "progressive_passes_per90": 0.20,
        "duels_won_pct": 0.15,
        "interceptions_per90": 0.15,
        "recoveries_per90": 0.15,
        "passes_per90": 0.10,
    },
    "Defender": {
        "interceptions_per90": 0.25,
        "duels_won_pct": 0.20,
        "recoveries_per90": 0.20,
        "pass_accuracy_pct": 0.15,
        "progressive_passes_per90": 0.10,
        "passes_per90": 0.10,
    },
    "Forward": {        # Dont have goals and assists YET
        "pass_accuracy_pct": 0.25,
        "progressive_passes_per90": 0.25,
        "passes_per90": 0.15,
        "duels_won_pct": 0.15,
        "recoveries_per90": 0.15,
        "interceptions_per90": 0.05,
    }
}

# Safety check: every group's weights must add up to 1
for group_name, group_weights in WEIGHTS.items():
    assert abs(sum(group_weights.values()) - 1) < 1e-9, f"{group_name} weights do not add up to 1"

def calculate_composite_rating(percentiles: dict, position_group: str):
    """
    Weighted rating from 0 to 10, built from a player's percentiles.

    Args:
        percentiles (dict): {metric_name: percentile 0-100}, as returned by get_percentiles.
        position_group (str): Midfielder, Defender, Forward or Goalkeeper.
    
    Returns:
        float: rating from 0 to 10, or None if it can't be calculated.
    """

    weights = WEIGHTS.get(position_group)
    if weights is None:
        return None

    total = 0
    used_weights = 0

    for metric, weight in weights.items():
        value = percentiles.get(metric)
        if value is None:   #Player has no data for this metric -> SKIP
            continue
        total += value * weight
        used_weights += weight

    if used_weights == 0:
        return None

    # Divide by the weight actually used, so a missing metric doesn't lower the rating
    # Divide by 10 to go rom 0-100 scale to 0-10
    return round(total / used_weights/ 10,2)