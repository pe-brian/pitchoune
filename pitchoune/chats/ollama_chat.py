import ollama

from pitchoune.chat import Chat


class OllamaChat(Chat):
    """Chat class for Ollama models."""
    def __init__(self, model: str, prompt: str, **params):
        super().__init__(model, prompt, **params)

    def send_msg(self, text: str) -> str:
        """Send a message to the chat and return the response."""
        return ollama.chat(
            model=self._model,
            messages=[
                {
                    "role": "system",
                    "content": self._prompt,
                }, {
                    "role": "user",
                    "content": text,
                },
            ],
            options={
                "temperature": self._params["temperature"],
                "max_tokens": self._params["max_tokens"]
            }
        ).message.content
