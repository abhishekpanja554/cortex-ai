from typing import Iterator

from google import genai
from google.genai import types
import logging

logger = logging.getLogger(__name__)

class GeminiChatClient:
    def __init__(self, api_key: str, model: str) -> None:
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def stream_answer(self, system_instruct: str, user_content: str) -> Iterator[str]:
        config = types.GenerateContentConfig(system_instruction=system_instruct)
        responses = self.client.models.generate_content_stream(
            model=self.model,
            contents=user_content,
            config=config
        )

        usage = None
        for chunk in responses:
            if chunk.text is not None:
                yield chunk.text
            if chunk.usage_metadata is not None:
                usage = chunk.usage_metadata

        if usage is not None:
            logger.info(
                "Gemini chat call (model=%s): %d prompt tokens, %d output tokens, %d total tokens",
                self.model,
                usage.prompt_token_count,
                usage.candidates_token_count,
                usage.total_token_count,
            )

    def create_chat(self, config: types.GenerateContentConfig):
        return self.client.chats.create(model=self.model, config=config)