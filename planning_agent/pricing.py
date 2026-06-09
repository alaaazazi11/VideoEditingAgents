from dataclasses import dataclass
from typing import Optional


@dataclass
class CostEstimate:
    feature: str
    cost: float
    details: str  # human readable explanation of how cost was calculated


def calculate_style_transfer_cost(duration_seconds: float) -> CostEstimate:
    """$0.10 per output video second"""
    cost = 0.10 * duration_seconds
    return CostEstimate(
        feature="style_transfer",
        cost=round(cost, 4),
        details=f"$0.10 × {duration_seconds}s = ${cost:.4f}"
    )


def calculate_outpainting_cost(duration_seconds: float) -> CostEstimate:
    """$0.08 per video second at 16fps"""
    cost = 0.08 * duration_seconds
    return CostEstimate(
        feature="outpainting",
        cost=round(cost, 4),
        details=f"$0.08 × {duration_seconds}s = ${cost:.4f}"
    )


def calculate_lip_sync_cost(duration_seconds: float) -> CostEstimate:
    """$8.00 per minute → $0.1333 per second"""
    cost = (8.00 / 60) * duration_seconds
    return CostEstimate(
        feature="lip_sync",
        cost=round(cost, 4),
        details=f"$8.00/min × {duration_seconds}s = ${cost:.4f}"
    )


def calculate_upscaling_cost(
    duration_seconds: float,
    width: int,
    height: int,
    fps: float = 30.0
) -> CostEstimate:
    """$0.001 per megapixel (width × height × frames)"""
    total_frames = duration_seconds * fps
    total_megapixels = (width * height * total_frames) / 1_000_000
    cost = 0.001 * total_megapixels
    return CostEstimate(
        feature="upscaling",
        cost=round(cost, 4),
        details=f"$0.001 × ({width}×{height}×{total_frames:.0f} frames) / 1M = ${cost:.4f}"
    )


def calculate_extend_duration_cost(added_seconds: float) -> CostEstimate:
    """$0.10 per added second"""
    cost = 0.10 * added_seconds
    return CostEstimate(
        feature="extend_duration",
        cost=round(cost, 4),
        details=f"$0.10 × {added_seconds}s added = ${cost:.4f}"
    )


def calculate_object_swap_cost(duration_seconds: float) -> CostEstimate:
    """
    ≤5s → $0.40
    >5s → $0.80
    """
    if duration_seconds <= 5:
        cost = 0.40
        details = f"Video ≤5s → flat rate $0.40"
    else:
        cost = 0.80
        details = f"Video >5s → flat rate $0.80"

    return CostEstimate(
        feature="object",
        cost=cost,
        details=details
    )


def calculate_background_removal_cost(compute_seconds: float) -> CostEstimate:
    """$0.00111 per compute second"""
    cost = 0.00111 * compute_seconds
    return CostEstimate(
        feature="background",
        cost=round(cost, 4),
        details=f"$0.00111 × {compute_seconds}s compute = ${cost:.4f}"
    )


def calculate_kling_cost(duration_seconds: float) -> CostEstimate:
    """$0.168 per video duration second"""
    cost = 0.168 * duration_seconds
    return CostEstimate(
        feature="kling",
        cost=round(cost, 4),
        details=f"$0.168 × {duration_seconds}s = ${cost:.4f}"
    )


# ─────────────────────────────────────────
# Main cost calculator
# ─────────────────────────────────────────

def calculate_feature_cost(
    feature: str,
    video_metadata: dict,
    extra_params: Optional[dict] = None
) -> CostEstimate:
    """
    Calculate cost for a single feature given video metadata.
    extra_params: optional additional info needed for cost calculation
    e.g. added_seconds for extend_duration, compute_seconds for background
    """
    duration = video_metadata.get("duration", 0)
    width = video_metadata.get("width", 1920)
    height = video_metadata.get("height", 1080)
    extra = extra_params or {}

    calculators = {
        "style_transfer": lambda: calculate_style_transfer_cost(duration),
        "outpainting": lambda: calculate_outpainting_cost(duration),
        "lip_sync": lambda: calculate_lip_sync_cost(duration),
        "upscaling": lambda: calculate_upscaling_cost(
            duration, width, height,
            extra.get("fps", 30.0)
        ),
        "extend_duration": lambda: calculate_extend_duration_cost(
            extra.get("added_seconds", 5.0)
        ),
        "object": lambda: calculate_object_swap_cost(duration),
        "background": lambda: calculate_background_removal_cost(
            extra.get("compute_seconds", duration * 2)  # estimate: 2x video duration
        ),
        "kling": lambda: calculate_kling_cost(duration),
    }

    if feature not in calculators:
        raise ValueError(f"Unknown feature: {feature}")

    return calculators[feature]()


def calculate_total_cost(estimates: list[CostEstimate]) -> float:
    """Sum up all feature costs"""
    return round(sum(e.cost for e in estimates), 4)


def compare_tiers(
    selected_features: list[str],
    video_metadata: dict,
    extra_params: Optional[dict] = None
) -> dict:
    """
    Compare Basic tier total cost vs Advanced tier (Kling) cost.
    Returns which is cheaper and by how much.
    """
    # calculate basic tier total
    basic_estimates = [
        calculate_feature_cost(f, video_metadata, extra_params)
        for f in selected_features
        if f != "kling"
    ]
    basic_total = calculate_total_cost(basic_estimates)

    # calculate advanced tier (kling)
    kling_estimate = calculate_kling_cost(video_metadata.get("duration", 0))
    kling_total = kling_estimate.cost

    cheaper_tier = "basic" if basic_total <= kling_total else "advanced"
    savings = abs(basic_total - kling_total)

    return {
        "basic_total": basic_total,
        "basic_estimates": basic_estimates,
        "kling_total": kling_total,
        "cheaper_tier": cheaper_tier,
        "savings": round(savings, 4),
    }