from routing_agent.features import get_features_summary


def get_decompose_prompt(user_prompt: str, video_metadata: dict) -> str:
    """
    Prompt for decomposing user prompt into atomic edits
    and matching each to a feature.
    """
    return f"""
You are a video editing assistant that analyzes user requests and breaks them down into atomic edits.

Here are all available video editing features:
{get_features_summary()}

Video metadata:
- Duration: {video_metadata.get('duration')} seconds
- Format: {video_metadata.get('format')}
- Width: {video_metadata.get('width')}px
- Height: {video_metadata.get('height')}px

User request:
"{user_prompt}"

Your job:
1. Break the user request into atomic edits — each edit is ONE specific transformation
2. Match each atomic edit to the most appropriate feature from the list above
3. Be careful — some params like 'aspect_ratio', 'resolution', 'audio_setting' are OPTIONS within a feature, NOT separate features

Rules:
- ONE atomic edit = ONE feature
- If the user mentions an aspect ratio change alongside a style change → it's ONE atomic edit (style_transfer), NOT two
- If the user mentions keeping audio → it's a param of the relevant feature, NOT lip_sync
- Only use lip_sync if the user explicitly wants to sync lips to a NEW audio track
- Only use object swap if the user provides or mentions a replacement image
- Only use background removal if the user wants the background removed/transparent
- Do NOT create atomic edits for params — only for actual transformations

Return ONLY a valid JSON object, no explanation or markdown:
{{
    "atomic_edits": [
        {{
            "edit_description": "plain english description of this edit",
            "matched_feature": "feature_name",
            "confidence": 0.95
        }}
    ]
}}
"""


def get_tier_decision_prompt(
    atomic_edits: list[dict],
    basic_total_cost: float,
    kling_total_cost: float,
    video_metadata: dict
) -> str:
    return f"""
You are a video editing cost optimizer. Your job is to decide whether to use Basic tier or Advanced tier (Kling).

IMPORTANT CONTEXT:
- Basic tier has SPECIALIZED models for each edit type (style transfer, upscaling, lip sync, etc.)
- ALL the features listed in the atomic edits below ARE supported by Basic tier
- Advanced tier (Kling) is ONE powerful model that can handle everything in a single call
- The ONLY reason to choose Advanced tier is if it's CHEAPER than Basic tier for multiple edits

Atomic edits requested:
{atomic_edits}

Cost comparison:
- Basic tier total: ${basic_total_cost:.4f}
- Advanced tier (Kling): ${kling_total_cost:.4f}

STRICT tier selection rules — follow exactly:
1. If there is ONLY ONE atomic edit → ALWAYS use Basic tier, regardless of cost
   - Basic tier has a specialized model for every single edit type
   - Never use Kling for a single edit
2. If there are MULTIPLE atomic edits:
   - If Basic total <= Kling cost → use Basic tier
   - If Kling cost < Basic total → use Advanced tier (Kling)

Return ONLY a valid JSON object:
{{
    "tier": "basic" or "advanced",
    "tier_reasoning": "plain english explanation",
    "selected_features": ["feature1", "feature2"] // basic features list, or ["kling"] for advanced
}}
"""


def get_replanning_prompt(
    user_prompt: str,
    user_feedback: str,
    previous_plan: dict,
    video_metadata: dict
) -> str:
    """
    Prompt for replanning after user requests changes.
    """
    return f"""
You are a video editing assistant. The user has reviewed the plan and requested changes.

Original user request:
"{user_prompt}"

Previous plan that was shown to user:
{previous_plan}

User feedback:
"{user_feedback}"

Video metadata:
- Duration: {video_metadata.get('duration')} seconds

Available features:
{get_features_summary()}

Your job:
1. Understand what the user wants to change based on their feedback
2. Adjust the selected features and/or tier accordingly
3. Common feedback patterns:
   - "too expensive" → try cheaper alternative or remove a feature
   - "remove X feature" → remove that feature from the plan
   - "use advanced tier" → switch to Kling
   - "use basic tier" → switch back to Basic
   - "add X feature" → add the requested feature

Return ONLY a valid JSON object:
{{
    "atomic_edits": [
        {{
            "edit_description": "plain english description",
            "matched_feature": "feature_name",
            "confidence": 0.95
        }}
    ],
    "changes_made": "plain english explanation of what changed from previous plan"
}}
"""