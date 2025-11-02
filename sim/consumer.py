import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Join the "chat" group so all users are in the same room
        await self.channel_layer.group_add("chat", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the chat group when someone disconnects
        await self.channel_layer.group_discard("chat", self.channel_name)

    async def receive(self, text_data):
        # Called when a message is received from a client
        data = json.loads(text_data)
        message = data["message"]
        user = data.get("user", "Anonymous")

        # Broadcast the message to everyone in the "chat" group
        await self.channel_layer.group_send(
            "chat",
            {
                "type": "chat_message",
                "message": message,
                "user": user,
            }
        )

    async def chat_message(self, event):
        # Send the message to WebSocket
        await self.send(text_data=json.dumps({
            "user": event["user"],
            "message": event["message"]
        }))
