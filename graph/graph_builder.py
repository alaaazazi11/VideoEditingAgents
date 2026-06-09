
from langgraph.graph import StateGraph, END
from state.shared_state import SharedState
from graph.nodes import (
    routing_agent_node,
    planning_agent_node,
    show_plan_node,
    run_feature_agents_node,
    merge_and_message_node,
    build_final_params_node,
    execution_agent_node,        # ← add
)
from graph.edges import (
    should_continue_or_finish,
    should_skip_planning_or_route,
    should_execute_or_failed,    # ← add
)

def build_graph() -> StateGraph:
    graph = StateGraph(SharedState)

    # ─────────────────────────────────────────
    # Add nodes
    # ─────────────────────────────────────────
    graph.add_node("router", lambda state: state)
    graph.add_node("routing_agent", routing_agent_node)
    graph.add_node("planning_agent", planning_agent_node)
    graph.add_node("show_plan", show_plan_node)
    graph.add_node("run_feature_agents", run_feature_agents_node)
    graph.add_node("merge_and_message", merge_and_message_node)
    graph.add_node("build_final_params", build_final_params_node)
    graph.add_node("execution_agent", execution_agent_node)  # ← add

    # ─────────────────────────────────────────
    # Entry point
    # ─────────────────────────────────────────
    graph.set_entry_point("router")
    graph.add_conditional_edges(
        "router",
        should_skip_planning_or_route,
        {
            "routing_agent": "routing_agent",
            "run_feature_agents": "run_feature_agents",
        }
    )

    # ─────────────────────────────────────────
    # Edges
    # ─────────────────────────────────────────
    graph.add_edge("routing_agent", "planning_agent")
    graph.add_edge("planning_agent", "show_plan")
    graph.add_edge("show_plan", END)

    graph.add_conditional_edges(
        "run_feature_agents",
        should_continue_or_finish,
        {
            "merge_and_message": "merge_and_message",
            "build_final_params": "build_final_params",
        }
    )

    graph.add_edge("merge_and_message", END)

    # build_final_params → execution_agent
    graph.add_edge("build_final_params", "execution_agent")  # ← add

    # execution_agent → done or failed → END
    graph.add_conditional_edges(
        "execution_agent",
        should_execute_or_failed,
        {
            "done": END,
            "failed": END,
        }
    )

    return graph.compile()