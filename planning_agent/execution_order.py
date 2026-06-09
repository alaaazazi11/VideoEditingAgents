from dataclasses import dataclass


# ─────────────────────────────────────────
# Execution Order
# ─────────────────────────────────────────

EXECUTION_ORDER: dict[str, int] = {
    "background": 1,      # structural changes first — remove/change background
    "object": 2,          # swap objects/persons before any style changes
    "lip_sync": 3,        # sync lips before visual transformations
    "extend_duration": 4, # extend video before applying style
    "outpainting": 5,     # expand frame before style transfer
    "style_transfer": 6,  # apply style after all structural changes
    "upscaling": 7,       # ALWAYS last — enhance final result
    "kling": 1,           # advanced tier — single step, always first
}


# ─────────────────────────────────────────
# Step model
# ─────────────────────────────────────────

@dataclass
class ExecutionStep:
    step_number: int
    feature: str
    display_name: str
    cost: float
    cost_details: str
    description: str     # human readable description of what this step does


# ─────────────────────────────────────────
# Display names
# ─────────────────────────────────────────

FEATURE_DISPLAY_NAMES: dict[str, str] = {
    "style_transfer": "Style Transfer",
    "outpainting": "Video Outpainting",
    "lip_sync": "Lip Sync",
    "upscaling": "Video Upscaling",
    "extend_duration": "Extend Duration",
    "object": "Object Swap",
    "background": "Background Removal",
    "kling": "Kling AI (Advanced)",
}


# ─────────────────────────────────────────
# Step descriptions
# ─────────────────────────────────────────

FEATURE_DESCRIPTIONS: dict[str, str] = {
    "style_transfer": "Apply visual style transformation across all frames",
    "outpainting": "Expand video frame beyond original aspect ratio",
    "lip_sync": "Synchronize character lip movements to audio track",
    "upscaling": "Enhance video resolution and quality",
    "extend_duration": "Generate additional frames to lengthen the video",
    "object": "Swap or replace objects, persons, or background",
    "background": "Remove or replace the video background",
    "kling": "Apply all requested edits using Kling AI in one step",
}


# ─────────────────────────────────────────
# Sorter
# ─────────────────────────────────────────

def sort_features_by_execution_order(features: list[str]) -> list[str]:
    """
    Sort features by their execution order.
    Returns sorted list — first feature should run first.
    """
    return sorted(
        features,
        key=lambda f: EXECUTION_ORDER.get(f, 99)
    )


def build_execution_steps(
    features: list[str],
    cost_estimates: list,  # list of CostEstimate from pricing.py
) -> list[ExecutionStep]:
    """
    Build ordered execution steps with cost info.
    Each step maps to one feature agent.
    """
    # sort features by execution order
    sorted_features = sort_features_by_execution_order(features)

    # build cost map for quick lookup
    cost_map = {e.feature: e for e in cost_estimates}

    steps = []
    for i, feature in enumerate(sorted_features, 1):
        estimate = cost_map.get(feature)
        steps.append(ExecutionStep(
            step_number=i,
            feature=feature,
            display_name=FEATURE_DISPLAY_NAMES.get(feature, feature),
            cost=estimate.cost if estimate else 0.0,
            cost_details=estimate.details if estimate else "N/A",
            description=FEATURE_DESCRIPTIONS.get(feature, ""),
        ))

    return steps