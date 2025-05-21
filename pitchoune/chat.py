class Chat:
    """Base class for chat models."""
    def __init__(self, model: str, prompt: str, **params):
        self._model = model
        self._prompt = prompt
        self._params = params
        if not "temperature" in self._params:
            self._params["temperature"] = 0.5
        if not "max_tokens" in self._params:
            self._params["max_tokens"] = 2048
        if not "top_p" in self._params:
            self._params["top_p"] = 1

    def send_msg(self, text: str) -> str:
        """Send a message to the chat and return the response."""
        raise NotImplementedError("send_msg method must be implemented in subclasses")
