from abc import ABC, abstractmethod
import asyncio
from typing import Any, Optional
import json
import logging

from state.shared_state import SharedState, AgentStatus


import os
from dotenv import load_dotenv
load_dotenv()



from openai import AsyncOpenAI
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# setup logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%H:%M:%S"
)

class BaseAgent(ABC):

    def __init__(self, feature_name: str, shared_state: SharedState):
        self.feature_name = feature_name
        self.shared_state = shared_state
        self.video_metadata = shared_state["video_metadata"]
        self.conversation_history = shared_state["conversation_history"]
        self.file_references = shared_state.get("file_references", {})
        self.logger = logging.getLogger(f"agent.{feature_name}")

    # ─────────────────────────────────────────
    # Abstract methods — each agent implements
    # ─────────────────────────────────────────

    @abstractmethod
    def get_schema(self) -> dict:
        pass

    @abstractmethod
    def get_validator(self):
        pass

    @abstractmethod
    def get_required_fields(self) -> list[str]:
        pass

    @abstractmethod
    def get_optional_fields(self) -> list[str]:
        pass

    @abstractmethod
    def get_valid_keys(self) -> set[str]:
        pass

    # ─────────────────────────────────────────
    # Core logic
    # ─────────────────────────────────────────

    async def extract_params(self, user_message: str) -> dict:
        schema = self.get_schema()
        valid_keys = self.get_valid_keys()

        extraction_prompt = f"""
You are a parameter extraction assistant for a video editing system.
Your job is to extract relevant parameters from the user's message for the '{self.feature_name}' feature.

Here is the parameter schema you need to extract:
{schema}

Video metadata (already available, do not ask user for these):
- URL: {self.video_metadata.get('url')}
- Format: {self.video_metadata.get('format')}
- Duration: {self.video_metadata.get('duration')} seconds
- Size: {self.video_metadata.get('size_mb')} MB

File references (resolve @placeholders to their actual URLs when extracting):
{self._format_file_references()}

STRICT RULES:
1. ONLY extract values explicitly stated or clearly implied by the user
2. If a value is not clearly mentioned, DO NOT include it in the JSON
3. Do NOT guess, assume, or infer values the user didn't provide
4. Do NOT include video_url — it is handled automatically
5. Return an empty JSON {{}} if nothing relevant was mentioned
6. Return ONLY a valid JSON object, no explanation or markdown
7. Do NOT wrap the JSON in markdown code blocks or backticks
8. Start your response directly with {{ and end with }}
9. Extract ALL values the user mentioned EVEN IF they seem invalid — validation is handled separately, your job is ONLY extraction
10. When you see @Video1, @Image1, @Image2 etc. in the prompt — resolve them to their actual URLs from the file references above
11. For 'kling' feature ONLY: NEVER include image URLs or resolved placeholder URLs inside the 'prompt' field — URLs belong ONLY in 'elements' or 'image_urls' fields. The prompt must contain plain English description of the edit only, with no URLs or @placeholders.

Conversation history:
{self._format_history()}
ء
Latest user message:
{user_message}
"""

        
        response = await client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=1000,
                messages=[{"role": "user", "content": extraction_prompt}]
                )
      
        try:
            raw = response.choices[0].message.content
            # clean markdown code blocks if LLM wraps in ```json
            raw = raw.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            raw = raw.strip()

            extracted = json.loads(raw)
            extracted = {k: v for k, v in extracted.items() if k in valid_keys}
            extracted["video_url"] = self.video_metadata.get("url")
            self.logger.info(f"Extracted params: {json.dumps(extracted, indent=2)}")
            return extracted
        except Exception as e:
            self.logger.error(f"Failed to parse extracted params: {e}")
            return {"video_url": self.video_metadata.get("url")}

    def get_missing_required_params(self, collected_params: dict) -> list[str]:
        required = self.get_required_fields()
        return [
            field for field in required
            if field not in collected_params or collected_params[field] is None
        ]

    async def run(self, user_message: str) -> dict:
        self.logger.info(f"Starting — processing user message")

        current_state = self.shared_state["agents_state"].get(
            self.feature_name,
            {
                "status": AgentStatus.COLLECTING,
                "collected_params": {},
                "missing_params": [],
                "invalid_params": []
            }
        )

        newly_extracted = await self.extract_params(user_message)
        collected_params = {**current_state["collected_params"], **newly_extracted}

        validator = self.get_validator()
        is_valid, errors = validator.validate(collected_params)

        missing = self.get_missing_required_params(collected_params)

        # log missing params
        if missing:
            self.logger.warning(f"Missing required params: {missing}")

        # log invalid params
        if errors:
            for error in errors:
                self.logger.warning(
                    f"Invalid param → '{error.param}': {error.reason} "
                    f"| valid options: {error.valid_options}"
                )

        if not missing and is_valid:
            status = AgentStatus.DONE
            self.logger.info(f"✅ Done — all params collected and valid")
        else:
            status = AgentStatus.COLLECTING
            self.logger.info(f"⏳ Still collecting — waiting for more info")

        return {
            "status": status,
            "collected_params": collected_params,
            "missing_params": missing,
            "invalid_params": [
                {
                    "param": e.param,
                    "reason": e.reason,
                    "valid_options": e.valid_options
                }
                for e in errors
            ]
        }

    # ─────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────

    def _format_history(self) -> str:
        """Format conversation history for LLM prompt"""
        if not self.conversation_history:
            return "No previous conversation"
        return "\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in self.conversation_history
        ])

    def _format_file_references(self) -> str:
        """Format file references for LLM prompt"""
        if not self.file_references:
            return "No file references available"
        return "\n".join([
            f"- {placeholder} = {url}"
            for placeholder, url in self.file_references.items()
        ])

    def is_done(self) -> bool:
        """Check if this agent has collected all required params"""
        state = self.shared_state["agents_state"].get(self.feature_name)
        if not state:
            return False
        return state["status"] == AgentStatus.DONE