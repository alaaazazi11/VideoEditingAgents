import streamlit as st


def plan_card(plan: dict) -> tuple[bool | None, str | None]:
    """
    Display the agent's plan with structured steps and confirm/reject buttons.
    Returns (confirmed: bool | None, feedback: str | None)
    """
    st.markdown("---")
    st.markdown("### 📋 Editing Plan")

    if plan:
        # ── Agent summary message
        if "summary" in plan:
            st.markdown(plan["summary"])

        # ── Structured steps
        steps = plan.get("steps", [])
        if steps:
            st.markdown("---")
            st.markdown("#### ⚙️ Execution Steps")

            for step in steps:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(
                        f"**Step {step['step_number']} — {step['display_name']}**  \n"
                        f"{step['description']}"
                    )
                with col2:
                    st.markdown(
                        f"<p style='text-align:right; font-weight:bold; color:#4CAF50'>"
                        f"${step['cost']:.4f}</p>",
                        unsafe_allow_html=True
                    )
                    if step.get("cost_details"):
                        st.caption(step["cost_details"])

            # ── Total cost
            st.markdown("---")
            total = plan.get("total_cost", 0.0)
            tier = plan.get("tier", "basic")
            tier_label = "🟡 Basic" if tier == "basic" else "🔴 Advanced (Kling)"

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Tier:** {tier_label}")
            with col2:
                st.markdown(
                    f"<p style='text-align:right; font-size:1.2em; font-weight:bold;'>"
                    f"💰 Total: ${total:.4f}</p>",
                    unsafe_allow_html=True
                )

    st.markdown("---")
    st.markdown("**Does this plan look good?**")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Confirm Plan", use_container_width=True, type="primary"):
            return True, None

    with col2:
        if st.button("🔄 Request Changes", use_container_width=True):
            st.session_state["show_feedback_input"] = True

    # feedback input
    if st.session_state.get("show_feedback_input"):
        feedback = st.text_area(
            "What would you like to change?",
            placeholder="e.g. Remove the subtitle feature, add background music instead",
            key="plan_feedback_input"
        )
        if st.button("Send Feedback", type="primary"):
            if feedback.strip():
                st.session_state["show_feedback_input"] = False
                return False, feedback.strip()
            else:
                st.warning("Please enter your feedback first.")

    return None, None