import asyncio
import logging
from execution_agent.agent import ExecutionAgent
from execution_agent.schemas import ExecutionAgentInput

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%H:%M:%S"
)

async def run_test(
    test_name: str,
    selected_features: list[str],
    final_params: dict,
    initial_video_url: str
):
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"Features: {selected_features}")
    print(f"{'='*60}")

    agent = ExecutionAgent()

    input = ExecutionAgentInput(
        final_params=final_params,
        selected_features=selected_features,
        initial_video_url=initial_video_url
    )

    output = await agent.run(input)

    print(f"\n📋 EXECUTION RESULT:")
    print(f"  Success: {output.success}")
    if output.error:
        print(f"  Error: {output.error}")
    print(f"  Final video URL: {output.final_video_url}")
    print(f"\n  Steps:")
    for step in output.steps:
        status = "✅" if step.success else "❌"
        print(f"  {status} {step.feature}")
        print(f"      Input:  {step.input_video_url}")
        print(f"      Output: {step.output_video_url}")
        if step.error:
            print(f"      Error:  {step.error}")

    return output


async def main():

    VIDEO_URL = "https://v3b.fal.media/files/b/0a940a70/s4jC3lmmbU8Q6xM-SFtWB_m5JJudvy.mp4"

    # ─────────────────────────────────────────
    # Case 1 — Single feature: Style Transfer
    # ─────────────────────────────────────────
    await run_test(
        test_name="Single feature — Style Transfer",
        selected_features=["style_transfer"],
        final_params={
            "style_transfer": {
                "prompt": "transform the video into a beautiful anime style",
                "video_url": VIDEO_URL,
                "resolution": "1080p",
                "audio_setting": "auto",
                "enable_safety_checker": True,
                "duration": 0,
            }
        },
        initial_video_url=VIDEO_URL
    )

    # ─────────────────────────────────────────
    # Case 2 — Two features: Style Transfer → Upscaling
    # ─────────────────────────────────────────
    await run_test(
        test_name="Two features — Style Transfer → Upscaling",
        selected_features=["style_transfer", "upscaling"],
        final_params={
            "style_transfer": {
                "prompt": "cinematic noir black and white style",
                "video_url": VIDEO_URL,
                "resolution": "720p",
                "audio_setting": "auto",
                "enable_safety_checker": True,
                "duration": 0,
            },
            "upscaling": {
                "video_url": VIDEO_URL,  # will be overridden by style_transfer output
                "upscale_mode": "factor",
                "upscale_factor": 2.0,
                "output_quality": "high",
                "output_format": "X264 (.mp4)",
                "output_write_mode": "balanced",
                "noise_scale": 0.1,
                "sync_mode": False,
            }
        },
        initial_video_url=VIDEO_URL
    )


if __name__ == "__main__":
    asyncio.run(main())