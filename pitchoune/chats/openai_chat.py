from openai import OpenAI

from pitchoune.chat import Chat


class OpenAIChat(Chat):
    """Chat class for OpenAI models."""
    def __init__(self, model: str, prompt: str, client: OpenAI, **params):
        self._client = client
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
