import json
from channels.generic.websocket import WebsocketConsumer

class TurnoConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        print("WebSocket conectado")

    def disconnect(self, close_code):
        print("WebSocket desconectado")

    def receive(self, text_data):
        data = json.loads(text_data)
        print(f"Datos recibidos: {data}")

        # Broadcast the data to all connected clients
        self.send(text_data=json.dumps({
            'message': data
        }))
