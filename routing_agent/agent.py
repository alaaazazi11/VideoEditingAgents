import json
import logging
import asyncio

from dotenv import load_dotenv
import os

from routing_agent.schemas import RoutingAgentInput, RoutingAgentOutput, AtomicEdit
from routing_agent.features import FEATURES_REGISTRY
from routing_agent.prompts import (
    get_decompose_prompt,
    get_tier_decision_prompt,
    get_replanning_prompt
)
from planning_agent.pricing import calculate_feature_cost, compare_tiers

load_dotenv()


from openai import AsyncOpenAI
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

logger = logging.getLogger("routing_agent")


class RoutingAgent:

    async def run(self, input: RoutingAgentInput) -> RoutingAgentOutput:
        """
        Main Routing Agent logic:
        1. Decompose user prompt into atomic edits
        2. Match each edit to a feature
        3. Calculate costs for Basic and Advanced tier
        4. Decide which tier to use
        5. Return routing output to Planning Agent
        """
        logger.info(f"🚀 Routing Agent started for prompt: {input.user_prompt[:50]}...")

        # ─────────────────────────────────────────
        # Step 1 — Decompose prompt into atomic edits
        # ─────────────────────────────────────────
        if input.user_feedback and input.previous_plan:
            # replanning after user feedback
            logger.info("🔄 Replanning based on user feedback")
            atomic_edits = await self._replan(input)
        else:
            # first time planning
            atomic_edits = await self._decompose(input)

        logger.info(f"📋 Atomic edits: {[e.matched_feature for e in atomic_edits]}")

        # ─────────────────────────────────────────
        # Step 2 — Calculate costs
        # ─────────────────────────────────────────
        selected_features = [e.matched_feature for e in atomic_edits]

        tier_comparison = compare_tiers(
            selected_features=selected_features,
            video_metadata=input.video_metadata
        )

        basic_total = tier_comparison["basic_total"]
        kling_total = tier_comparison["kling_total"]

        logger.info(f"💰 Basic tier: ${basic_total:.4f} | Kling: ${kling_total:.4f}")

        # ─────────────────────────────────────────
        # Step 3 — Decide tier
        # ─────────────────────────────────────────
        tier_decision = await self._decide_tier(
            atomic_edits=[e.model_dump() for e in atomic_edits],
            basic_total_cost=basic_total,
            kling_total_cost=kling_total,
            video_metadata=input.video_metadata
        )

        tier = tier_decision["tier"]
        tier_reasoning = tier_decision["tier_reasoning"]
        final_features = tier_decision["selected_features"]

        logger.info(f"✅ Tier decision: {tier} → features: {final_features}")
        logger.info(f"📝 Reasoning: {tier_reasoning}")

        return RoutingAgentOutput(
            user_prompt=input.user_prompt,
            atomic_edits=atomic_edits,
            selected_features=final_features,
            tier=tier,
            tier_reasoning=tier_reasoning,
            basic_total_cost=basic_total,
            kling_total_cost=kling_total,
            video_metadata=input.video_metadata,
            file_references=input.file_references
        )

    # ─────────────────────────────────────────
    # Private methods
    # ─────────────────────────────────────────

    async def _decompose(self, input: RoutingAgentInput) -> list[AtomicEdit]:
        """Decompose user prompt into atomic edits"""
        prompt = get_decompose_prompt(
            user_prompt=input.user_prompt,
            video_metadata=input.video_metadata
        )

      
        response = await client.chat.completions.create(
                     model="gpt-4o-mini",
                     max_tokens=1000,
                     messages=[{"role": "user", "content": prompt}]
                        )

        try:
            raw = response.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            raw = raw.strip()

            data = json.loads(raw)
            atomic_edits = [
                AtomicEdit(**edit)
                for edit in data["atomic_edits"]
            ]
            return atomic_edits

        except Exception as e:
            logger.error(f"❌ Failed to decompose prompt: {e}")
            raise

    async def _replan(self, input: RoutingAgentInput) -> list[AtomicEdit]:
        """Replan based on user feedback"""
        prompt = get_replanning_prompt(
            user_prompt=input.user_prompt,
            user_feedback=input.user_feedback,
            previous_plan=input.previous_plan,
            video_metadata=input.video_metadata
        )

        
        response = await client.chat.completions.create(
    model="gpt-4o-mini",
    max_tokens=1000,
    messages=[{"role": "user", "content": prompt}]
)

        try:
            raw = response.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            raw = raw.strip()

            data = json.loads(raw)
            atomic_edits = [
                AtomicEdit(**edit)
                for edit in data["atomic_edits"]
            ]

            logger.info(f"🔄 Changes made: {data.get('changes_made', '')}")
            return atomic_edits

        except Exception as e:
            logger.error(f"❌ Failed to replan: {e}")
            raise

    async def _decide_tier(
        self,
        atomic_edits: list[dict],
        basic_total_cost: float,
        kling_total_cost: float,
        video_metadata: dict
    ) -> dict:
        """Decide Basic vs Advanced tier"""
        prompt = get_tier_decision_prompt(
            atomic_edits=atomic_edits,
            basic_total_cost=basic_total_cost,
            kling_total_cost=kling_total_cost,
            video_metadata=video_metadata
        )

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            raw = response.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            raw = raw.strip()

            return json.loads(raw)

        except Exception as e:
            logger.error(f"❌ Failed to decide tier: {e}")
            raise