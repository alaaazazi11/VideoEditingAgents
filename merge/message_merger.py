import json
import logging
import asyncio

from state.shared_state import SharedState, AgentStatus
from schemas.style_transfer_schema import StyleTransferParams
from schemas.lip_sync_schema import LipSyncParams
from schemas.upscaling_schema import UpscalingParams
from schemas.extend_duration_schema import ExtendDurationParams
from schemas.object_schema import ObjectParams
from schemas.background_schema import BackgroundParams
from schemas.outpainting_schema import OutpaintingParams

import os
from dotenv import load_dotenv
load_dotenv()

from openai import AsyncOpenAI
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

logger = logging.getLogger("merger")

# ─────────────────────────────────────────
# Agent Registry
# ─────────────────────────────────────────
from agents.style_transfer_agent import StyleTransferAgent
from agents.lip_sync_agent import LipSyncAgent
from agents.upscaling_agent import UpscalingAgent
from agents.extend_duration_agent import ExtendDurationAgent
from agents.object_agent import ObjectAgent
from agents.background_agent import BackgroundAgent
from agents.outpainting_agent import OutpaintingAgent
from agents.kling_agent import KlingAgent
from schemas.kling_schema import KlingParams

AGENT_REGISTRY = {
    "style_transfer": StyleTransferAgent,
    "lip_sync": LipSyncAgent,
    "upscaling": UpscalingAgent,
    "extend_duration": ExtendDurationAgent,
    "object": ObjectAgent,
    "background": BackgroundAgent,
    "outpainting": OutpaintingAgent,
    "kling": KlingAgent,
}


class MessageMerger:

    def __init__(self, shared_state: SharedState):
        self.shared_state = shared_state

    def collect_issues(self) -> dict[str, dict]:
        """
        Collect missing and invalid params from all non-done agents.
        Enriches missing params with their schema descriptions.
        """
        issues = {}

        for feature_name, agent_state in self.shared_state["agents_state"].items():
            if agent_state["status"] == AgentStatus.DONE:
                continue

            missing = agent_state.get("missing_params", [])
            invalid = agent_state.get("invalid_params", [])

            if not missing and not invalid:
                continue

            # get schema descriptions for missing params
            agent_class = AGENT_REGISTRY[feature_name]
            agent = agent_class(self.shared_state)
            schema = agent.get_schema()
            properties = schema.get("properties", {})

            missing_with_desc = [
                {
                    "param": param,
                    "description": properties.get(param, {}).get("description", param)
                }
                for param in missing
            ]

            issues[feature_name] = {
                "missing": missing_with_desc,
                "invalid": invalid
            }

            logger.info(
                f"Issues for '{feature_name}' → "
                f"missing: {[p['param'] for p in missing_with_desc]} | "
                f"invalid: {[e['param'] for e in invalid]}"
            )

        return issues

    def all_done(self) -> bool:
        """Check if all agents are done"""
        return all(
            state["status"] == AgentStatus.DONE
            for state in self.shared_state["agents_state"].values()
        )

    async def merge(self) -> str:
        """
        Merge all agents' missing/invalid params into one natural message to the user.
        Uses LLM to generate a friendly, natural message.
        """
        issues = self.collect_issues()

        if not issues:
            return ""

        merge_prompt = f"""
You are a friendly video editing assistant helping a user complete their video editing request.

The user has made a request and you need to ask them for some missing information or correct some invalid values.

Here are the issues that need to be resolved:
{json.dumps(issues, indent=2)}

Each missing param includes:
- "param": the technical parameter name (never show this to the user)
- "description": what this parameter means in plain English (use this to ask the user)

Each invalid param includes:
- "param": the technical parameter name (never show this to the user)
- "reason": why it's invalid
- "valid_options": the correct options to choose from

Rules:
1. Write a single, natural, friendly message to the user
2. NEVER mention technical parameter names or feature names
3. Use the description to ask about missing params in plain English
4. For invalid params, mention what went wrong and show valid options friendly
5. Group everything naturally into one flowing message
6. Keep it concise — don't overwhelm the user
7. Sound like a helpful human assistant, not a robot
8. Do NOT number or bullet point every single param — weave them naturally

Example tone:
"Almost there! I just need a couple more details — could you share 
a link to the image you'd like to swap into the video? Also, the 
resolution you entered isn't supported — you can choose from 720p or 1080p."
"""

        response = await client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=1000,
                messages=[{"role": "user", "content": merge_prompt}]
            )
        logger.info(f"📩 Generated message to user: {response.choices[0].message.content   }")
        return response.choices[0].message.content

    def build_final_params(self) -> dict:
        """
        Build the final params dict from all done agents.
        Merges user provided values with schema defaults.
        Sent to Execution Agent when all agents are done.
        """
        final_params = {}

        schema_map = {
            "style_transfer": StyleTransferParams,
            "lip_sync": LipSyncParams,
            "upscaling": UpscalingParams,
            "extend_duration": ExtendDurationParams,
            "object": ObjectParams,
            "background": BackgroundParams,
            "outpainting": OutpaintingParams,
             "kling": KlingParams,
        }

        for feature_name, agent_state in self.shared_state["agents_state"].items():
            if agent_state["status"] == AgentStatus.DONE:

                # get defaults from pydantic schema
                schema_class = schema_map[feature_name]
                defaults = {
                    name: field.default
                    for name, field in schema_class.model_fields.items()
                    if field.default is not None
                }

                # merge: defaults first, user provided values override
                final_params[feature_name] = {
                    **defaults,
                    **agent_state["collected_params"]
                }

        return final_params

