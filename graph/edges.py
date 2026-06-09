from state.shared_state import SharedState
from merge.message_merger import MessageMerger


def should_continue_or_finish(state: SharedState) -> str:
    """After feature agents run — check if all done"""
    merger = MessageMerger(state)
    if merger.all_done():
        return "build_final_params"
    else:
        return "merge_and_message"


def should_replan_or_collect(state: SharedState) -> str:
    """
    After user gives feedback on plan:
    - changes_requested → back to routing agent
    - confirmed → start collecting params
    """
    plan_status = state.get("plan_status", "awaiting_confirmation")
    if plan_status == "confirmed":
        return "run_feature_agents"
    else:
        return "routing_agent"


def should_skip_planning_or_route(state: SharedState) -> str:
    """Entry point edge — skip routing/planning if already confirmed"""
    if state.get("skip_planning") and state.get("plan_status") == "confirmed":
        return "run_feature_agents"
    else:
        return "routing_agent"   


def should_execute_or_failed(state: SharedState) -> str:
    """After execution — check if succeeded or failed"""
    if state.get("execution_status") == "done":
        return "done"
    else:
        return "failed"     