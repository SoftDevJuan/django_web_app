import json
from channels.generic.websocket import AsyncWebsocketConsumer

class TurnosConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("turnos", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("turnos", self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        # Procesar los datos recibidos, si es necesario

    async def send_turnos(self, event):
        await self.send(text_data=json.dumps(event["turnos"]))
