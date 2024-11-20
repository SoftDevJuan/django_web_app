from rest_framework import serializers

class ConteoCiudadanosSerializer(serializers.Serializer):
    dia = serializers.DateField()
    cantidad_ciudadanos = serializers.IntegerField()
    total_general = serializers.IntegerField()