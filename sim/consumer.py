import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from . import models
from Stupid_hack_transform import transform


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("chat", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("chat", self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]
        user = data.get("user", "Anonymous")

        message = await self.transform_message(message)
        await self.save_message(user, message)

        await self.channel_layer.group_send(
            "chat",
            {
                "type": "chat_message",
                "message": message,
                "user": user,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "user": event["user"],
            "message": event["message"],
        }))

    @database_sync_to_async
    def transform_message(self, message):
        return transform(message)

    @database_sync_to_async
    def save_message(self, username, content):
        author, _ = models.Author.objects.get_or_create(name=username)
        models.Message.objects.create(author=author, content=content)
