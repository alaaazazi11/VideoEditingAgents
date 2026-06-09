import asyncio
import json
import logging
from state.shared_state import SharedState, AgentStatus
from merge.message_merger import MessageMerger, AGENT_REGISTRY

# ← add these imports
from routing_agent.agent import RoutingAgent
from routing_agent.schemas import RoutingAgentInput
from planning_agent.agent import PlanningAgent
from planning_agent.schemas import PlanningAgentInput

from execution_agent.agent import ExecutionAgent
from execution_agent.schemas import ExecutionAgentInput

logger = logging.getLogger("graph")

# ─────────────────────────────────────────
# NEW — Routing Agent Node
# ─────────────────────────────────────────

async def routing_agent_node(state: SharedState) -> SharedState:
    """
    Runs the Routing Agent.
    Decomposes user prompt into atomic edits and decides tier + features.
    """
    logger.info("🚀 Routing Agent node started")

    agent = RoutingAgent()
    routing_input = RoutingAgentInput(
        user_prompt=state["user_prompt"],
        video_metadata=state["video_metadata"],
        file_references=state.get("file_references", {}),
        user_feedback=state.get("user_plan_feedback"),
        previous_plan=state.get("plan")
    )

    output = await agent.run(routing_input)

    # update shared state with routing output
    state["selected_features"] = output.selected_features
    state["tier"] = output.tier
    state["tier_reasoning"] = output.tier_reasoning
    state["basic_total_cost"] = output.basic_total_cost
    state["kling_total_cost"] = output.kling_total_cost

    logger.info(f"✅ Routing done → tier: {output.tier} | features: {output.selected_features}")

    return state


# ─────────────────────────────────────────
# NEW — Planning Agent Node
# ─────────────────────────────────────────

async def planning_agent_node(state: SharedState) -> SharedState:
    """
    Runs the Planning Agent.
    Builds execution plan with costs and generates user-friendly summary.
    """
    logger.info("📋 Planning Agent node started")

    agent = PlanningAgent()
    planning_input = PlanningAgentInput(
        user_prompt=state["user_prompt"],
        selected_features=state["selected_features"],
        tier=state["tier"],
        video_metadata=state["video_metadata"],
        user_feedback=state.get("user_plan_feedback"),
        previous_plan=state.get("plan")
    )

    output = await agent.run(planning_input)

    # update shared state with plan
    state["plan"] = output.plan.model_dump()
    state["plan_status"] = output.status
    state["latest_assistant_message"] = output.plan.summary

    # update conversation history
    state["conversation_history"].append({
        "role": "assistant",
        "content": output.plan.summary
    })

    logger.info(f"✅ Plan ready → total cost: ${output.plan.total_cost:.4f}")

    return state


# ─────────────────────────────────────────
# NEW — Show Plan Node
# ─────────────────────────────────────────

def show_plan_node(state: SharedState) -> SharedState:
    """
    Waits for user confirmation on the plan.
    Just sets status — main.py handles actual user input.
    """
    logger.info(f"⏳ Waiting for user confirmation on plan")
    state["plan_status"] = "awaiting_confirmation"
    return state


# ─────────────────────────────────────────
# EXISTING — Feature Agents Node
# ─────────────────────────────────────────

async def run_feature_agents_node(state: SharedState) -> SharedState:
    selected_features = state["selected_features"]
    latest_user_reply = state.get("latest_user_reply") or state["user_prompt"]

    logger.info(f"🚀 Running feature agents: {selected_features}")

    if not state.get("agents_state"):
        state["agents_state"] = {
            feature: {
                "status": AgentStatus.COLLECTING,
                "collected_params": {},
                "missing_params": [],
                "invalid_params": []
            }
            for feature in selected_features
        }

    agents_to_run = [
        feature for feature in selected_features
        if state["agents_state"][feature]["status"] != AgentStatus.DONE
    ]

    logger.info(f"⏳ Pending agents: {agents_to_run}")

    async def run_single_agent(feature_name: str):
        agent_class = AGENT_REGISTRY[feature_name]
        agent = agent_class(state)
        return feature_name, await agent.run(latest_user_reply)

    results = await asyncio.gather(*[
        run_single_agent(feature)
        for feature in agents_to_run
    ])

    for feature_name, agent_state in results:
        state["agents_state"][feature_name] = agent_state

    logger.info("📊 Agents status after run:")
    for feature, agent_state in state["agents_state"].items():
        logger.info(
            f"  → {feature}: {agent_state['status']} | "
            f"missing: {agent_state['missing_params']} | "
            f"invalid: {[e['param'] for e in agent_state['invalid_params']]}"
        )

    return state


# ─────────────────────────────────────────
# EXISTING — Merge and Message Node
# ─────────────────────────────────────────

async def merge_and_message_node(state: SharedState) -> SharedState:
    logger.info("💬 Merging agent reports into user message")

    merger = MessageMerger(state)
    message = await merger.merge()

    state["conversation_history"].append({
        "role": "assistant",
        "content": message
    })
    state["latest_assistant_message"] = message

    return state


# ─────────────────────────────────────────
# EXISTING — Build Final Params Node
# ─────────────────────────────────────────

def build_final_params_node(state: SharedState) -> SharedState:
    merger = MessageMerger(state)
    final_params = merger.build_final_params()
    state["final_params"] = final_params

    logger.info("✅ All agents done! Final params built:")
    for feature, params in final_params.items():
        logger.info(f"  → {feature}: {json.dumps(params, indent=2)}")

    return state


# ─────────────────────────────────────────
# EXISTING — Update User Reply
# ─────────────────────────────────────────

def update_user_reply(state: SharedState, user_reply: str) -> SharedState:
    logger.info(f"👤 User replied: {user_reply}")
    state["latest_user_reply"] = user_reply
    state["conversation_history"].append({
        "role": "user",
        "content": user_reply
    })
    return state



async def execution_agent_node(state: SharedState) -> SharedState:
    """
    Runs the Execution Agent.
    Executes all features sequentially using fal.ai API.
    """
    logger.info("🎬 Execution Agent node started")

    try:
        agent = ExecutionAgent()

        # get ordered features from plan
        plan = state.get("plan", {})
        selected_features = plan.get("selected_features", state["selected_features"])

        input = ExecutionAgentInput(
            final_params=state["final_params"],
            selected_features=selected_features,
            initial_video_url=state["video_metadata"]["url"]
        )

        output = await agent.run(input)

        if output.success:
            state["execution_status"] = "done"
            state["execution_output_url"] = output.final_video_url
            state["execution_error"] = None
            state["execution_steps"] = [s.model_dump() for s in output.steps]
            logger.info(f"✅ Execution done → {output.final_video_url}")
        else:
            state["execution_status"] = "failed"
            state["execution_output_url"] = ""
            state["execution_error"] = output.error
            state["execution_steps"] = [s.model_dump() for s in output.steps]
            logger.error(f"❌ Execution failed → {output.error}")

    except Exception as e:
        error = f"Unexpected error in Execution Agent: {str(e)}"
        logger.error(f"❌ {error}")
        state["execution_status"] = "failed"
        state["execution_output_url"] = ""
        state["execution_error"] = error
        state["execution_steps"] = []

    return state
