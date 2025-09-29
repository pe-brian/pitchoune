class Chat:
    """Base class for chat models."""
    def __init__(
        self,
        model: str,
        prompt: str = None,
        **params
    ):
        self._model = model
        self._prompt = prompt
        self._params = params

    def send_msg(
        self, text: str,
        prompt: str = None
    ) -> str:
        """Send a message to the chat and return the response."""
        raise NotImplementedError("send_msg method must be implemented in subclasses")
