from pitchoune.chat import Chat


openai = None
try:
    from openai import OpenAI
    openai = OpenAI()
except ImportError:
    pass


class OpenAIChat(Chat):
    """ Chat class for OpenAI models.
    """
    def __init__(
        self,
        model: str,
        prompt: str = None,
        **params
    ):
        if openai is None:
            print("Warning: The OPENAI_API_KEY environment variable is not set.")
        self._client = openai
        super().__init__(model=model, prompt=prompt, **params)

    def send_msg(
        self,
        text: str,
        prompt: str = None
    ) -> str:
        """ Send a message to the chat and return the response.
        """
        if self._client is None:
            raise Exception("Cannot create an OpenAI client without a valid OPENAI_API_KEY !")
        return self._client.chat.completions.create(
            model = self._params["model"],
            messages=[
                {
                    "role": "system",
                    "content": self._prompt or prompt
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
        ).choices[0].message.content
