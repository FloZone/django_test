import datetime
import logging

from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views import generic
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

import requests

from .models import Message
from .permissions import IsOwnerOrAdminOrReadOnly
from .serializers import MessageSerializer, UserSerializer


logger = logging.getLogger("firstapp")


####################
# Views
####################


class IndexView(generic.ListView):
    """
    View for index.html page.
    """

    template_name = 'firstapp/index.html'
    context_object_name = 'message_list'

    def get_queryset(self):
        """ Return all published messages. """
        return Message.objects.order_by('-publication_date')


class DetailView(generic.DetailView):
    """
    View for detail.html page.
    """

    model = Message
    template_name = 'firstapp/detail.html'
    context_object_name = 'message'


####################
# Actions
####################


def logout_user(request):
    """
    Log out the connected user.
    """

    logout(request)
    return HttpResponseRedirect(reverse("firstapp:index"))


####################
# REST framework
####################


class RestMessageView(viewsets.ModelViewSet):
    """
    REST API message view. Edit available for connected owners or admins.
    """

    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrAdminOrReadOnly,)

    def create(self, request, *args, **kwargs):
        """
        Validate the data in order to create the object.
        """
        logger.info('Message.create')
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        Perform the object creation.
        """
        # Add the owner and the publication date
        serializer.save(owner=self.request.user, publication_date=datetime.datetime.now())
        logger.info('Message.perform_create: new message saved')
        # Notify tornado
        r = requests.post('http://localhost:1234/message_update', data={'data': 'create'})
        logger.info('Tornado notified: %s' % r.status_code)

    def list(self, request, *args, **kwargs):
        """
        Return the list all of messages. Diff with get_queryset ?
        """
        logger.info('Message.list')
        message_list = super().list(request, *args, **kwargs)
        if len(message_list.data) == 0:
            return Response('No messages are available.')
        else:
            return message_list

    def get_queryset(self):
        """
        Return the list all of messages. Diff with list ?
        """
        logger.info('Message.get_queryset')
        return super().get_queryset().order_by('-publication_date')

    def destroy(self, request, *args, **kwargs):
        """
        Validate the data in order to delete the object.
        """
        logger.info('Message.destroy')
        return super().destroy(request, *args, **kwargs)

    def perform_destroy(self, instance):
        """
        Perform the object deletion.
        """
        super().perform_destroy(instance)
        logger.info('Message.perform_destroy')
        # Notify tornado
        r = requests.post('http://localhost:1234/message_update', data={'data': 'delete'})
        logger.info('Tornado notified: %s' % r.status_code)


class RestUserView(viewsets.ModelViewSet):
    """
    REST API user view. Read for authenticated, edit for owners or admins.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser,)
