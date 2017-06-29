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
from tornado_websockets.websocket import WebSocket

from .models import Message, Answer
from .permissions import IsOwnerOrAdminOrReadOnly
from .serializers import MessageSerializer, AnswerSerializer, UserSerializer

# Websockets
#############


# Make a new instance of WebSocket and automatically add handler '/ws/my_ws' to Tornado handlers
my_ws = WebSocket('/my_ws')

@my_ws.on
def open(socket, data):
    """ Automatically called when a new client connects. """
    print('New connection')

@my_ws.on
def close(socket, data):
    """ Automatically called when a client disconnects. """
    print('Disconnection')


@my_ws.on
def error(socket, data):
    """ Automatically called when an error occurs. """
    print(data)


@my_ws.on
def ping(socket, data):
    print('Receive PING %s' % data.get('message'))
    print('Send PONG')
    my_ws.emit("pong", "from server")


# Views
#############


class IndexView(generic.ListView):
    template_name = 'firstapp/index.html'
    context_object_name = 'message_list'

    def get_queryset(self):
        """ Return all published messages. """
        return Message.objects.order_by('-publication_date')


class DetailView(generic.DetailView):
    """ Display detail view. """
    model = Message
    template_name = 'firstapp/detail.html'
    context_object_name = 'message'


# Action
#############


def logout_user(request):
    """ Log out the connected user. """
    logout(request)
    return HttpResponseRedirect(reverse("firstapp:index"))


def post(request):
    """ Post a new message. """
    message_text = request.POST['message_text']
    if 0 < len(message_text) <= 140:
        new_message = Message(owner=request.user, message_text=message_text, publication_date=datetime.datetime.now())
        new_message.save()
        return HttpResponse()
    else:
        return HttpResponseBadRequest("Message length must be > 0 & <= 140 ")


def get_message(request):
    """ Get the complete messages list. """
    if request.method == 'GET':
        message_list = Message.objects.order_by('-publication_date')
        context = {
            'message_list': message_list,
        }
        return render(request, "firstapp/message_list.html", context)
    else:
        return HttpResponseBadRequest("GET method only")


def answer(request, message_id):
    """ Answer to a message. """
    message = get_object_or_404(Message, pk=message_id)
    answer_text = request.POST['answer_text']
    if 0 < len(answer_text) <= 140:
        new_answer = Answer(owner=request.user, message=message, answer_text=answer_text,
                            publication_date=datetime.datetime.now())
        new_answer.save()
        return HttpResponse()
    else:
        return HttpResponseBadRequest("Answer length must be > 0 & <= 140 ")


def get_answer(request, message_id):
    """ Get the complete enswers list. """
    if request.method == 'GET':
        message = get_object_or_404(Message, pk=message_id)
        context = {
            'message': message,
        }
        return render(request, "firstapp/answer_list.html", context)
    else:
        return HttpResponseBadRequest("GET method only")


def delete_message(request):
    """ Delete a message. """
    if request.method == 'POST':
        message_id = request.POST['message_id']
        message = get_object_or_404(Message, pk=message_id)
        message.delete()
        return HttpResponse()
    else:
        return HttpResponseBadRequest("POST method only")


def delete_answer(request):
    """ Delete an answer. """
    if request.method == 'POST':
        answer_id = request.POST['answer_id']
        answer = get_object_or_404(Answer, pk=answer_id)
        answer.delete()
        return HttpResponse()
    else:
        return HttpResponseBadRequest("POST method only")


# REST framework
#############


# class RestMessageList(APIView):
#     def get(self, request):
#         messages = Message.objects.all()
#         serializer = MessageSerializer(messages, many=True)
#         return Response(serializer.data)
#
#     def post(self, request):
#         serializer = MessageSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# class RestMessageDetail(APIView):
#     def get_object(self, pk):
#         try:
#             return Message.objects.get(pk=pk)
#         except Message.DoesNotExist:
#             raise Http404
#
#     def get(self, request, pk):
#         message = self.get_object(pk)
#         serializer = MessageSerializer(message)
#         return Response(serializer.data)
#
#     def delete(self, request, pk):
#         message = self.get_object(pk)
#         message.delete()
#         return HttpResponse(status=status.HTTP_204_NO_CONTENT)


@my_ws.on
class RestMessageView(viewsets.ModelViewSet):
    """
    REST API message view. Read for authenticated, edit for owners or admins
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrAdminOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user, publication_date=datetime.datetime.now())
        logging.debug('RestMessageView.perform_create: new message saved')

    def list(self, request, *args, **kwargs):
        logging.debug('RestMessageView.list')
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        logging.debug('RestMessageView.create')
        return super().create(request, *args, **kwargs)


class RestAnswerView(viewsets.ModelViewSet):
    """ REST API answer view. Read for authenticated, edit for owners or admins """
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrAdminOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user, publication_date=datetime.datetime.now())
        logging.debug('RestAnswerView.perform_create: new message saved')


class RestUserView(viewsets.ModelViewSet):
    """ REST API user view. Read for authenticated, edit for owners or admins """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser,)
