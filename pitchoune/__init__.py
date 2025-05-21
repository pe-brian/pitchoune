from pitchoune.factories.chat_factory import ChatFactory
from pitchoune.factories.io_factory import IOFactory
from pitchoune.super_factory import SuperFactory

super_factory = SuperFactory()

base_io_factory = super_factory.create(IOFactory)
base_chat_factory = super_factory.create(ChatFactory)
