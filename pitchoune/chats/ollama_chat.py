from pitchoune.chat import Chat


class OllamaChat(Chat):
    """ Chat class for Ollama models.
    """
    def __init__(
        self,
        model: str,
        prompt: str = None,
        **params
    ):
        super().__init__(model=model, prompt=prompt, **params)

    def send_msg(
        self,
        text: str,
        prompt: str = None
    ) -> str:
        """ Send a message to the chat and return the response.
        """
        if prompt:
            self._prompt = prompt
        
        import ollama
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
            options=self._params
        ).message.content
