from dataclasses import dataclass, field


# ─────────────────────────────────────────
# Feature Definition
# ─────────────────────────────────────────

@dataclass
class FeatureDefinition:
    name: str
    display_name: str
    description: str                    # what this feature does
    trigger_words: list[str]            # words/phrases that indicate this feature
    cannot_handle: list[str]            # things this feature CANNOT do
    requires: list[str]                 # required inputs beyond video_url
    tier: str                           # basic or advanced


# ─────────────────────────────────────────
# Features Registry
# ─────────────────────────────────────────

FEATURES_REGISTRY: dict[str, FeatureDefinition] = {

    "style_transfer": FeatureDefinition(
        name="style_transfer",
        display_name="Style Transfer",
        description="Applies a visual style transformation across all frames of the video. Changes how the video LOOKS without changing its content or structure.",
        trigger_words=[
            "anime", "cartoon", "oil painting", "watercolor", "cinematic",
            "vintage", "noir", "black and white", "artistic", "style",
            "look like", "transform into", "make it look", "visual style",
            "drawing", "illustration", "painting", "retro", "classic",
            "aesthetic", "filter", "effect", "stylize"
        ],
        cannot_handle=[
            "adding or removing objects",
            "changing background",
            "extending video duration",
            "expanding frame size",
            "syncing audio to lips",
            "increasing resolution"
        ],
        requires=[],
        tier="basic"
    ),

    "outpainting": FeatureDefinition(
        name="outpainting",
        display_name="Video Outpainting",
        description="Expands the video frame beyond its original boundaries by generating new content on the sides, top, or bottom. Changes the aspect ratio or adds more scene around the original content.",
        trigger_words=[
            "widen", "expand", "extend sides", "outpaint", "un-crop",
            "wider", "more space", "add sides", "horizontal", "vertical",
            "aspect ratio", "16:9", "9:16", "widescreen", "portrait",
            "open up", "zoom out", "show more", "landscape", "tiktok format",
            "youtube format", "reels format", "fill the sides", "add background"
        ],
        cannot_handle=[
            "changing visual style",
            "removing objects",
            "syncing audio",
            "increasing resolution",
            "extending video duration in time"
        ],
        requires=["prompt for expanded areas"],
        tier="basic"
    ),

    "lip_sync": FeatureDefinition(
        name="lip_sync",
        display_name="Lip Sync",
        description="Synchronizes a character's lip movements in the video to match a provided audio track.",
        trigger_words=[
            "lip sync", "sync lips", "mouth movement", "make him say",
            "make her say", "speak", "talking", "audio track", "voice",
            "sync audio", "match audio", "dubbing", "dub", "speech",
            "words", "dialogue", "narration"
        ],
        cannot_handle=[
            "changing visual style",
            "removing objects",
            "expanding frame",
            "increasing resolution",
            "extending video duration"
        ],
        requires=["audio_url"],
        tier="basic"
    ),

    "upscaling": FeatureDefinition(
        name="upscaling",
        display_name="Video Upscaling",
        description="Enhances video resolution and quality. Makes the video sharper and higher quality.",
        trigger_words=[
            "upscale", "enhance", "higher resolution", "better quality",
            "sharper", "clearer", "4K", "1080p", "HD", "2K", "increase resolution",
            "improve quality", "enhance quality", "resolution boost",
            "make it clearer", "make it sharper"
        ],
        cannot_handle=[
            "changing visual style",
            "removing objects",
            "expanding frame",
            "syncing audio",
            "extending duration"
        ],
        requires=[],
        tier="basic"
    ),

    "extend_duration": FeatureDefinition(
        name="extend_duration",
        display_name="Extend Duration",
        description="Generates new frames and appends them to the start or end of the video to make it longer.",
        trigger_words=[
            "extend", "longer", "add seconds", "more time", "continue",
            "lengthen", "add frames", "make it longer", "append",
            "add to the end", "add to the start", "extend duration",
            "add more", "continuation", "keep going"
        ],
        cannot_handle=[
            "changing visual style",
            "removing objects",
            "expanding frame size",
            "syncing audio",
            "increasing resolution"
        ],
        requires=["prompt describing continuation"],
        tier="basic"
    ),

    "object": FeatureDefinition(
        name="object",
        display_name="Object Swap",
        description="Swaps or replaces a person, object, or background in the video with a provided image.",
        trigger_words=[
            "swap", "replace", "change the person", "change the face",
            "change the object", "change the car", "change the background",
            "substitute", "put instead", "swap out", "replace with",
            "change to", "use this image instead", "put this person",
            "face swap", "object replacement"
        ],
        cannot_handle=[
            "adding completely new objects that don't exist",
            "removing objects without replacement",
            "changing visual style",
            "expanding frame",
            "syncing audio",
            "increasing resolution"
        ],
        requires=["image_url for replacement"],
        tier="basic"
    ),

    "background": FeatureDefinition(
        name="background",
        display_name="Background Removal",
        description="Detects and removes the background from the video, isolating the foreground subject with a transparent background.",
        trigger_words=[
            "remove background", "transparent background", "isolate",
            "cut out", "foreground only", "no background", "green screen",
            "chroma key", "background removal", "extract subject",
            "separate background", "clean background"
        ],
        cannot_handle=[
            "replacing background with specific image — only removes it",
            "changing visual style",
            "swapping objects",
            "expanding frame",
            "syncing audio",
            "increasing resolution"
        ],
        requires=[],
        tier="basic"
    ),

    "kling": FeatureDefinition(
        name="kling",
        display_name="Kling AI (Advanced)",
        description="A powerful advanced AI model that handles complex video edits that Basic tier models cannot handle, or when using Kling is cheaper than combining multiple Basic tier models.",
        trigger_words=[],  # Kling is chosen by cost comparison or complexity, not trigger words
        cannot_handle=[],  # Kling can handle anything
        requires=["prompt"],
        tier="advanced"
    ),
}


# ─────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────

def get_all_basic_features() -> list[FeatureDefinition]:
    """Return all Basic tier features"""
    return [f for f in FEATURES_REGISTRY.values() if f.tier == "basic"]


def get_feature(name: str) -> FeatureDefinition:
    """Get a feature by name"""
    if name not in FEATURES_REGISTRY:
        raise ValueError(f"Unknown feature: {name}")
    return FEATURES_REGISTRY[name]


def get_features_summary() -> str:
    """
    Returns a formatted summary of all features for LLM prompt.
    Helps Routing Agent understand what each feature does.
    """
    lines = []
    for name, feature in FEATURES_REGISTRY.items():
        if name == "kling":
            continue  # kling is chosen by cost, not by trigger words
        lines.append(f"""
Feature: {feature.display_name} (name: '{name}')
Description: {feature.description}
Trigger words/phrases: {', '.join(feature.trigger_words[:10])}
Cannot handle: {', '.join(feature.cannot_handle[:3])}
Requires: {', '.join(feature.requires) if feature.requires else 'nothing extra'}
""")
    return "\n".join(lines)