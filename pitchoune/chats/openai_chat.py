import os
from openai import OpenAI

from pitchoune.chat import Chat


openai = None
try:
    openai = OpenAI()
except ImportError:
    pass


class OpenAIChat(Chat):
    """Chat class for OpenAI models."""
    def __init__(self, model: str, prompt: str, **params):
        if openai is None:
            raise ImportError("The OPENAI_API_KEY environment variable is not set.")
        self._client = openai
        super().__init__(model, prompt, **params)

    def send_msg(self, text: str) -> str:
        """Send a message to the chat and return the response."""
        return self._client.responses.create(
            instructions=self._prompt,
            input=text,
            model=self._model,
            temperature=0,
            max_output_tokens=2048
        ).output_text
