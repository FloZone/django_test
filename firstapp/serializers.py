from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Message, Answer


class UserSerializer(serializers.ModelSerializer):
    message_set = serializers.PrimaryKeyRelatedField(many=True, queryset=Message.objects.all())
    answer_set = serializers.PrimaryKeyRelatedField(many=True, queryset=Answer.objects.all())

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'message_set', 'answer_set')


class MessageSerializer(serializers.ModelSerializer):
    answer_set = serializers.PrimaryKeyRelatedField(many=True, queryset=Answer.objects.all())

    class Meta:
        model = Message
        fields = ('id', 'owner', 'message_text', 'publication_date', 'answer_set')
        extra_kwargs = {
            'owner': {'read_only': True},
            'publication_date': {'read_only': True},
        }


class AnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer
        fields = ('id', 'owner', 'message', 'answer_text', 'publication_date')
        extra_kwargs = {
            'owner': {'read_only': True},
            'publication_date': {'read_only': True},
        }
