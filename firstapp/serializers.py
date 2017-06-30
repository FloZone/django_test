from rest_framework import serializers
from rest_framework.reverse import reverse
from django.contrib.auth.models import User
import pytz

from .models import Message


class UserSerializer(serializers.ModelSerializer):
    message_set = serializers.PrimaryKeyRelatedField(many=True, queryset=Message.objects.all())

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'message_set')


class CustomDatetimeField(serializers.DateTimeField):
    def to_representation(self, value):
        #return value.strftime('%Y-%m-%d %H:%M:%S %Z%z')
        return value.strftime('%Y-%m-%d %H:%M:%S')


class MessageSerializer(serializers.ModelSerializer):
    publication_date = CustomDatetimeField(required=False)
    link = serializers.SerializerMethodField()

    def get_link(self, obj):
        return {
            # url for detail html page
            'detail': reverse('firstapp:detail', args=[obj.id], request=self.context['request']),
            # url for rest api
            'delete': reverse('firstapp:rest:message-detail', args=[obj.id], request=self.context['request']),
        }

    class Meta:
        model = Message
        fields = ('id', 'owner', 'message_text', 'publication_date', 'link')
        extra_kwargs = {
            'owner': {'read_only': True},
            'publication_date': {'read_only': True},
        }
