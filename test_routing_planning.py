import asyncio
import logging

from routing_agent.agent import RoutingAgent
from routing_agent.schemas import RoutingAgentInput
from planning_agent.agent import PlanningAgent
from planning_agent.schemas import PlanningAgentInput

# setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%H:%M:%S"
)

# ─────────────────────────────────────────
# Test video metadata
# ─────────────────────────────────────────
VIDEO_METADATA = {
    "url": "https://fal.media/files/video/hero.mp4",
    "format": "mp4",
    "duration": 8.0,
    "size_mb": 45.0,
    "width": 1920,
    "height": 1080,
}

FILE_REFERENCES = {
    "@Video1": "https://fal.media/files/video/hero.mp4",
    "@Image1": "https://fal.media/files/images/style_ref.jpg",
}


async def run_test(user_prompt: str, test_name: str):
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"PROMPT: {user_prompt}")
    print(f"{'='*60}")

    routing_agent = RoutingAgent()
    planning_agent = PlanningAgent()

    # ─────────────────────────────────────────
    # Step 1 — Routing Agent
    # ─────────────────────────────────────────
    routing_input = RoutingAgentInput(
        user_prompt=user_prompt,
        video_metadata=VIDEO_METADATA,
        file_references=FILE_REFERENCES,
    )

    routing_output = await routing_agent.run(routing_input)

    print(f"\n📋 ROUTING OUTPUT:")
    print(f"  Tier: {routing_output.tier}")
    print(f"  Selected features: {routing_output.selected_features}")
    print(f"  Basic total: ${routing_output.basic_total_cost:.4f}")
    print(f"  Kling total: ${routing_output.kling_total_cost:.4f}")
    print(f"  Reasoning: {routing_output.tier_reasoning}")
    print(f"  Atomic edits:")
    for edit in routing_output.atomic_edits:
        print(f"    - {edit.edit_description} → {edit.matched_feature} (confidence: {edit.confidence})")

    # ─────────────────────────────────────────
    # Step 2 — Planning Agent
    # ─────────────────────────────────────────
    planning_input = PlanningAgentInput(
        user_prompt=user_prompt,
        selected_features=routing_output.selected_features,
        tier=routing_output.tier,
        video_metadata=VIDEO_METADATA,
    )

    planning_output = await planning_agent.run(planning_input)

    print(f"\n📋 PLAN:")
    print(f"  Tier: {planning_output.plan.tier}")
    print(f"  Total cost: ${planning_output.plan.total_cost:.4f}")
    print(f"  Steps:")
    for step in planning_output.plan.steps:
        print(f"    Step {step.step_number}: {step.display_name} — ${step.cost:.4f}")
        print(f"      {step.cost_details}")
    print(f"\n  Summary shown to user:")
    print(f"  {planning_output.plan.summary}")
    print(f"\n  Status: {planning_output.status}")


async def main():







    await run_test(
        user_prompt="Swap the dog in this video with the cat from @Image1, then outpaint the canvas from the top, with more sky and clouds extending above.",
        test_name="Object swap + outpainting"
    )


if __name__ == "__main__":
    asyncio.run(main())