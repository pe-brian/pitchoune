from pitchoune.chat import Chat
from pitchoune.chats.ollama_chat import OllamaChat
from pitchoune.chats.openai_chat import OpenAIChat
from pitchoune.factory import Factory


class ChatFactory(Factory):
    """Factory class to create chat instances."""
    def __init__(self, model: str=None, prompt: str=None, local: bool=False, params: dict = None):
        super().__init__(base_class=Chat, model=model, prompt=prompt, local=local, params=params)

    def create(self, *args, local: bool=False, **kwargs):
        """Create an instance of the chat class."""
        factory_local = self._kwargs["local"] if "local" in self._kwargs else local
        local =  factory_local or local
        cls = OllamaChat if local else OpenAIChat
        return super().create(cls, *args, **kwargs)
