from rest_framework import serializers


class PaymentsSerializer(serializers.Serializer):
    mdOrder = serializers.CharField(max_length=100)
    orderNumber = serializers.CharField(max_length=50)
    operation = serializers.CharField(max_length=50)
    callbackCreationDate = serializers.CharField(max_length=50)
    status = serializers.IntegerField()


class OuterPaymentsContentSerializer(serializers.Serializer):
    _content_type = serializers.CharField(max_length=50)
    _content = serializers.CharField()