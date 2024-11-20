# consumers.py
import json
from channels.generic.websocket import WebsocketConsumer

class ExpedienteConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'call_expediente':
            expediente_id = data.get('expediente_id')
            expediente_details = {
                'id': expediente_id,
                'sala': '22',
                'audiencia': '27391/2024',
                'conciliador': 'Si AGUILAR ELIZONDO',
                'solicitante': 'Juan Sebastian Aguirre Siordia',
                'citado': 'Jose Rigoberto Aguirre Siordia'
            }
            self.send(text_data=json.dumps({
                'type': 'expediente_details',
                'expediente': expediente_details
            }))
