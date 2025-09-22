from pitchoune.chat import Chat


openai = None
try:
    from openai import OpenAI
    openai = OpenAI()
except ImportError:
    pass


class OpenAIChat(Chat):
    """Chat class for OpenAI models."""
    def __init__(self, model: str, prompt: str = None, **params):
        if openai is None:
            raise ImportError("The OPENAI_API_KEY environment variable is not set.")
        self._client = openai
        super().__init__(model=model, prompt=prompt, **params)

    def send_msg(self, text: str, prompt: str = None) -> str:
        """Send a message to the chat and return the response."""
        if prompt:
            self._prompt = prompt
        return self._client.responses.create(
            instructions=self._prompt,
            input=text,
            model=self._model,
            temperature=0,
            max_output_tokens=2048
        ).output_text
