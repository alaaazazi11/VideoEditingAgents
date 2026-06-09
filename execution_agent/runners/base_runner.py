from abc import ABC, abstractmethod
import logging
import asyncio
import os
import fal_client
from dotenv import load_dotenv

load_dotenv()

# set fal key
os.environ["FAL_KEY"] = os.getenv("FAL_KEY", "")

logger = logging.getLogger("execution_agent")


class BaseRunner(ABC):

    def __init__(self, feature_name: str, endpoint: str):
        self.feature_name = feature_name
        self.endpoint = endpoint
        self.logger = logging.getLogger(f"runner.{feature_name}")

    @abstractmethod
    def build_input(self, params: dict) -> dict:
        """
        Build the exact input dict the fal.ai API expects.
        Filters out None values and maps param names if needed.
        """
        pass

    def extract_output_url(self, result: dict) -> str:
        """
        Extract output video URL from fal.ai response.
        All models return response["video"]["url"]
        """
        try:
            return result["video"]["url"]
        except KeyError as e:
            raise ValueError(f"Could not extract video URL from response: {result}") from e

    async def run(self, params: dict) -> str:
        """
        Run the model on fal.ai and return the output video URL.
        """
        self.logger.info(f"🚀 Running {self.feature_name} on {self.endpoint}")
        self.logger.info(f"Input video: {params.get('video_url')}")

        # build input for this specific model
        input_data = self.build_input(params)

        # remove None values — fal.ai doesn't like None params
        input_data = {k: v for k, v in input_data.items() if v is not None}

        self.logger.info(f"Calling fal.ai with params: {list(input_data.keys())}")

        try:
            # run on fal.ai — using asyncio.to_thread since fal_client is sync
            result = await asyncio.to_thread(
                fal_client.subscribe,
                self.endpoint,
                arguments=input_data,
                with_logs=True,
                on_queue_update=self._on_queue_update
            )

            output_url = self.extract_output_url(result)
            self.logger.info(f"✅ {self.feature_name} done → output: {output_url}")
            return output_url

        except Exception as e:
            self.logger.error(f"❌ {self.feature_name} failed: {e}")
            raise

    def _on_queue_update(self, update):
        """Log fal.ai queue updates"""
        if hasattr(update, 'logs'):
            for log in update.logs:
                self.logger.info(f"  [fal.ai] {log.get('message', '')}")