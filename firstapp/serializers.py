from rest_framework import serializers
from rest_framework.reverse import reverse
import pytz

from .models import Message, Author


class AuthorSerializer(serializers.ModelSerializer):
    message_set = serializers.PrimaryKeyRelatedField(many=True, queryset=Message.objects.all())

    class Meta:
        model = Author
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'timezone', 'message_set')


class CustomDatetimeField(serializers.DateTimeField):
    def to_representation(self, value):
        # If the user is authenticated, display the publication date with the correct timezone
        if self.context['request'].user.is_authenticated():
            timezone = self.context['request'].user.timezone
            value = value.astimezone(pytz.timezone(timezone))

        #return value.strftime('%Y-%m-%d %H:%M:%S %Z%z')
        return value.strftime('%Y-%m-%d %H:%M:%S %Z%z')


class MessageSerializer(serializers.ModelSerializer):
    publication_date = CustomDatetimeField(required=False)
    link = serializers.SerializerMethodField()

    def get_link(self, obj):
        links = {
            # url for message detail html page
            'detail': reverse('firstapp:message-detail', args=[obj.id], request=self.context['request']),
        }

        # add a 'delete' link if the connected user is the author or an admin
        if self.context['request'].user.is_staff or self.context['request'].user.id == obj.author.id:
            # url for rest api deletion
            links['delete'] = reverse('firstapp:rest:message-detail', args=[obj.id], request=self.context['request'])

        return links

    class Meta:
        model = Message
        fields = ('id', 'author', 'message_text', 'publication_date', 'link')
        extra_kwargs = {
            'author': {'read_only': True},
            'publication_date': {'read_only': True},
        }
