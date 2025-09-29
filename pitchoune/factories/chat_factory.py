from pitchoune.chat import Chat
from pitchoune.chats.ollama_chat import OllamaChat
from pitchoune.chats.openai_chat import OpenAIChat
from pitchoune.factory import Factory


class ChatFactory(Factory):
    """ Factory class to create chat instances.
    """
    def __init__(
        self
    ):
        super().__init__(base_class=Chat)

    def create(
        self,
        *args,
        local: bool=False,
        **kwargs
    ):
        """ Create an instance of the chat class.
        """
        return super().create(OllamaChat if local else OpenAIChat, *args, **kwargs)
