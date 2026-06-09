import json
import logging
import asyncio

from dotenv import load_dotenv
import os

from planning_agent.schemas import (
    PlanningAgentInput,
    PlanningAgentOutput,
    Plan,
    PlanStep
)
from planning_agent.pricing import (
    calculate_feature_cost,
    calculate_total_cost,
    compare_tiers
)
from planning_agent.execution_order import (
    sort_features_by_execution_order,
    build_execution_steps,
    FEATURE_DISPLAY_NAMES,
    FEATURE_DESCRIPTIONS
)
from planning_agent.prompts import (
    get_plan_summary_prompt,
    get_replan_summary_prompt
)

load_dotenv()
from openai import AsyncOpenAI
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

logger = logging.getLogger("planning_agent")


class PlanningAgent:

    async def run(self, input: PlanningAgentInput) -> PlanningAgentOutput:
        """
        Main Planning Agent logic:
        1. Take routing output
        2. Sort features by execution order
        3. Calculate cost per step
        4. Generate human friendly summary
        5. Return plan to show user
        """
        logger.info(f"🚀 Planning Agent started for features: {input.selected_features}")

        # ─────────────────────────────────────────
        # Step 1 — Calculate costs
        # ─────────────────────────────────────────
        cost_estimates = [
            calculate_feature_cost(feature, input.video_metadata)
            for feature in input.selected_features
        ]
        total_cost = calculate_total_cost(cost_estimates)

        # ─────────────────────────────────────────
        # Step 2 — Build ordered execution steps
        # ─────────────────────────────────────────
        execution_steps = build_execution_steps(
            features=input.selected_features,
            cost_estimates=cost_estimates
        )

        # ─────────────────────────────────────────
        # Step 3 — Generate human friendly summary
        # ─────────────────────────────────────────
        tier_comparison = compare_tiers(
            selected_features=input.selected_features,
            video_metadata=input.video_metadata
        )

        if input.user_feedback and input.previous_plan:
            # replanning summary
            summary = await self._generate_replan_summary(
                user_prompt=input.user_prompt,
                user_feedback=input.user_feedback,
                tier=input.tier,
                steps=[self._step_to_dict(s) for s in execution_steps],
                total_cost=total_cost,
                changes_made=input.previous_plan.get("changes_made", "")
            )
        else:
            # first time summary
            summary = await self._generate_summary(
                user_prompt=input.user_prompt,
                tier=input.tier,
                steps=[self._step_to_dict(s) for s in execution_steps],
                total_cost=total_cost,
                basic_total_cost=tier_comparison["basic_total"],
                kling_total_cost=tier_comparison["kling_total"],
                tier_reasoning=input.previous_plan.get("tier_reasoning", "") if input.previous_plan else ""
            )

        logger.info(f"📋 Plan generated — {len(execution_steps)} steps — total: ${total_cost:.4f}")
        logger.info(f"📝 Summary: {summary[:100]}...")

        # ─────────────────────────────────────────
        # Step 4 — Build plan output
        # ─────────────────────────────────────────
        plan = Plan(
            tier=input.tier,
            steps=[
                PlanStep(
                    step_number=s.step_number,
                    feature=s.feature,
                    display_name=s.display_name,
                    cost=s.cost,
                    cost_details=s.cost_details,
                    description=s.description
                )
                for s in execution_steps
            ],
            total_cost=total_cost,
            summary=summary,
            selected_features=[s.feature for s in execution_steps]
        )

        return PlanningAgentOutput(
            plan=plan,
            status="awaiting_confirmation"
        )

    # ─────────────────────────────────────────
    # Private methods
    # ─────────────────────────────────────────

    async def _generate_summary(
        self,
        user_prompt: str,
        tier: str,
        steps: list[dict],
        total_cost: float,
        basic_total_cost: float,
        kling_total_cost: float,
        tier_reasoning: str
    ) -> str:
        """Generate human friendly plan summary"""
        prompt = get_plan_summary_prompt(
            user_prompt=user_prompt,
            tier=tier,
            steps=steps,
            total_cost=total_cost,
            basic_total_cost=basic_total_cost,
            kling_total_cost=kling_total_cost,
            tier_reasoning=tier_reasoning
        )

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()

    async def _generate_replan_summary(
        self,
        user_prompt: str,
        user_feedback: str,
        tier: str,
        steps: list[dict],
        total_cost: float,
        changes_made: str
    ) -> str:
        """Generate human friendly summary after replanning"""
        prompt = get_replan_summary_prompt(
            user_prompt=user_prompt,
            user_feedback=user_feedback,
            tier=tier,
            steps=steps,
            total_cost=total_cost,
            changes_made=changes_made
        )


        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()

    def _step_to_dict(self, step) -> dict:
        """Convert ExecutionStep to dict for prompt"""
        return {
            "step_number": step.step_number,
            "feature": step.feature,
            "display_name": step.display_name,
            "cost": step.cost,
            "cost_details": step.cost_details,
            "description": step.description
        }