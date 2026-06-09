import asyncio
import logging
from graph.graph_builder import build_graph
from graph.nodes import update_user_reply
from state.shared_state import SharedState

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%H:%M:%S"
)

async def run(
    user_prompt: str,
    video_metadata: dict,
    file_references: dict = {},
) -> dict:

    initial_state: SharedState = {
        "user_prompt": user_prompt,
        "video_metadata": video_metadata,
        "file_references": file_references,
        "selected_features": [],
        "tier": "",
        "tier_reasoning": "",
        "basic_total_cost": 0.0,
        "kling_total_cost": 0.0,
        "plan": None,
        "plan_status": "awaiting_confirmation",
        "skip_planning": False,
        "user_plan_feedback": None,
        "agents_state": {},
        "conversation_history": [
            {"role": "user", "content": user_prompt}
        ],
        "latest_user_reply": user_prompt,
        "latest_assistant_message": "",
        "final_params": {} ,

        "execution_status": "pending",      # بيبدأ بـ pending كحالة ابتدائية منطقية
        "execution_output_url": "",         # سترينج فاضي تماماً بدون مسافات عشان قيمته المنطقية تكون False
        "execution_error": None,            # None ممتاز جداً هنا
        "execution_steps": []             # لستة فاضية جاهزة للـ append


    }

    graph = build_graph()
    state = initial_state

    while True:
        # استدعاء الـ Graph بالـ State الحالية
        state = await graph.ainvoke(state)

        # ─────────────────────────────────────────
        # 1. Check Execution Success
        # ─────────────────────────────────────────
        if state.get("execution_status") == "done":
            print("\n🎉 Video processing complete!")
            print(f"📹 Final video URL: {state['execution_output_url']}")
            print("\n📋 Execution steps:")
            for step in state.get("execution_steps", []):
                status = "✅" if step["success"] else "❌"
                print(f"  {status} {step['feature']} → {step['output_video_url']}")
            return state["execution_output_url"]
        
        # ─────────────────────────────────────────
        # 2. Check Execution Failure
        # ─────────────────────────────────────────
        if state.get("execution_status") == "failed":
            print(f"\n❌ Video processing failed!")
            print(f"Error: {state.get('execution_error')}")
            print("\n📋 Steps that ran:")
            for step in state.get("execution_steps", []):
                status = "✅" if step["success"] else "❌"
                print(f"  {status} {step['feature']}")
                if not step["success"]:
                    print(f"      Error: {step['error']}")
            return None

        # ─────────────────────────────────────────
        # 3. Notification: Params collected & Execution started
        # (شيلنا الـ return من هنا عشان يكمل للـ execution)
        # ─────────────────────────────────────────
        if state.get("final_params") and state.get("execution_status") not in ["done", "failed"]:
            print("\n✅ All params collected! Execution Agent is processing the video layers...")

        # ─────────────────────────────────────────
        # 4. Show plan — wait for user confirmation
        # ─────────────────────────────────────────
        if state.get("plan_status") == "awaiting_confirmation":
            print(f"\n🤖 Assistant: {state['latest_assistant_message']}")
            print("\n[1] Confirm   [2] Request Changes")
            user_input = input("\n👤 You: ").strip()

            if user_input == "1" or "confirm" in user_input.lower():
                state["plan_status"] = "confirmed"
                state["skip_planning"] = True
                state["user_plan_feedback"] = None
                state["agents_state"] = {}
                state["latest_user_reply"] = state["user_prompt"]
                state["conversation_history"].append({
                    "role": "user",
                    "content": "Confirmed — original request: " + state["user_prompt"]
                })
            else:
                state["plan_status"] = "changes_requested"
                state["skip_planning"] = False
                state["user_plan_feedback"] = user_input
                state["latest_user_reply"] = user_input
                state["conversation_history"].append({
                    "role": "user",
                    "content": user_input
                })
            
           
            state["latest_assistant_message"] = ""
            continue

        # ─────────────────────────────────────────
        # 5. Show message — wait for user reply (Param Collection)
        # ─────────────────────────────────────────
        assistant_message = state.get("latest_assistant_message", "")
        if assistant_message:
            print(f"\n🤖 Assistant: {assistant_message}")
            user_reply = input("\n👤 You: ").strip()
            state = update_user_reply(state, user_reply)
            state["latest_assistant_message"] = "" # تصفير الرسالة بعد الرد عليها


if __name__ == "__main__":
    asyncio.run(run(
        user_prompt="Swap the dog in this video with the cat from @Image1. Change the style i mean time of day to a dramatic golden hour sunset where warm orange and pink light bathes the entire scene, long shadows stretch across the grass, and lens flare reflects from the low sun in the background. Deliver the final output in cinematic high quality.",
        video_metadata={
            "url": "https://fal.media/files/video/hero.mp4",
            "format": "mp4",
            "duration": 8.0,
            "size_mb": 45.0,
            "width": 1920,
            "height": 1080,
        },
        file_references={
            "@Video1": "https://fal.media/files/video/hero.mp4",
            "@Image1": "https://fal.media/files/images/style_ref.jpg",
        }
    ))