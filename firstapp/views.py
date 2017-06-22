import datetime

from django.shortcuts import get_object_or_404, render
from django.views import generic
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponse
from django.contrib.auth import logout

from tornado_websockets.websocket import WebSocket

from .models import Message, Answer


# Create your views here.


# Index view based on generic.listview
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


# Websockets


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
def message_event(socket, data):
    print('Receive message: %s' % data)
    if 'PING' in data.get('message'):
        message = data.get('message').replace("PING", "PONG")
        print('Send message: %s' % message)
        my_ws.emit("message_event", message)
