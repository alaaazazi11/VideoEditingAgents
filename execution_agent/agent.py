import logging
from execution_agent.schemas import (
    ExecutionAgentInput,
    ExecutionAgentOutput,
    StepResult
)
from execution_agent.runners.style_transfer_runner import StyleTransferRunner
from execution_agent.runners.lip_sync_runner import LipSyncRunner
from execution_agent.runners.upscaling_runner import UpscalingRunner
from execution_agent.runners.extend_duration_runner import ExtendDurationRunner
from execution_agent.runners.object_runner import ObjectRunner
from execution_agent.runners.background_runner import BackgroundRunner
from execution_agent.runners.outpainting_runner import OutpaintingRunner
from execution_agent.runners.kling_runner import KlingRunner

logger = logging.getLogger("execution_agent")

# ─────────────────────────────────────────
# Runner Registry
# ─────────────────────────────────────────

RUNNER_REGISTRY = {
    "style_transfer": StyleTransferRunner,
    "lip_sync": LipSyncRunner,
    "upscaling": UpscalingRunner,
    "extend_duration": ExtendDurationRunner,
    "object": ObjectRunner,
    "background": BackgroundRunner,
    "outpainting": OutpaintingRunner,
    "kling": KlingRunner,
}


class ExecutionAgent:

    async def run(self, input: ExecutionAgentInput) -> ExecutionAgentOutput:
        """
        Execute all features sequentially in order.
        Output video URL of each step becomes the input for the next step.
        """
        logger.info(f"🚀 Execution Agent started")
        logger.info(f"Features to execute: {input.selected_features}")

        current_video_url = input.initial_video_url
        steps: list[StepResult] = []

        for feature in input.selected_features:
            logger.info(f"\n{'='*50}")
            logger.info(f"▶️  Executing step: {feature}")
            logger.info(f"Input video URL: {current_video_url}")

            # get params for this feature
            params = input.final_params.get(feature, {})

            # always use the latest video URL — overrides collected param
            params["video_url"] = current_video_url

            # get runner for this feature
            runner_class = RUNNER_REGISTRY.get(feature)
            if not runner_class:
                error = f"No runner found for feature: {feature}"
                logger.error(f"❌ {error}")
                steps.append(StepResult(
                    feature=feature,
                    input_video_url=current_video_url,
                    output_video_url="",
                    success=False,
                    error=error
                ))
                return ExecutionAgentOutput(
                    final_video_url="",
                    steps=steps,
                    success=False,
                    error=error
                )

            # run the model
            runner = runner_class()
            try:
                output_url = await runner.run(params)

                steps.append(StepResult(
                    feature=feature,
                    input_video_url=current_video_url,
                    output_video_url=output_url,
                    success=True
                ))

                # update current video URL for next step
                current_video_url = output_url
                logger.info(f"✅ Step {feature} complete → {output_url}")

            except Exception as e:
                error = str(e)
                logger.error(f"❌ Step {feature} failed: {error}")
                steps.append(StepResult(
                    feature=feature,
                    input_video_url=current_video_url,
                    output_video_url="",
                    success=False,
                    error=error
                ))
                # stop everything on failure
                return ExecutionAgentOutput(
                    final_video_url="",
                    steps=steps,
                    success=False,
                    error=f"Step '{feature}' failed: {error}"
                )

        logger.info(f"\n{'='*50}")
        logger.info(f"🎉 All steps complete!")
        logger.info(f"Final video URL: {current_video_url}")

        return ExecutionAgentOutput(
            final_video_url=current_video_url,
            steps=steps,
            success=True
        )