import datetime
import logging
import requests
import pytz

from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext

from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .models import Message, Author
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import MessageSerializer, AuthorSerializer


logger = logging.getLogger("firstapp")


####################
# Views
####################


def index(request):
    """
    View for index.html page.
    """
    return render(request, 'firstapp/index.html')


def message_detail(request, message_id):
    """
    View for message.html page.
    """
    return render(request, 'firstapp/message.html', {'message_id': message_id})


def author_detail(request, author_id):
    """
    View for author.html page.
    """
    # give data to the template
    author = get_object_or_404(Author, id=author_id)
    context = {
        'author': author,
        'timezones': pytz.common_timezones,
    }

    # If the timezone form is submitted (by an admin)
    try:
        if request.method == 'POST':
            if request.user.is_staff:
                timezone = request.POST['timezone']
                author.timezone = timezone
                author.save()
                logging.info("Timezone updated for %s by %s" % (author.username, request.user.username))
                # add info to the template
                # Translators: Toast message when timezone is successfully updated
                context['info'] = gettext("Timezone updated :)")
            else:
                logging.info("WARNING: a non-admin user (%s) try to update the timezone for %s" % (author.username, request.user.username))
    except Exception as e:
        logging.info("ERROR: exception while updating the timezone: %s" % e)
    return render(request, 'firstapp/author.html', context)


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
    REST API message view. Edit available for connected authors or admins.
    """

    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsAuthorOrAdminOrReadOnly,)

    def create(self, request, *args, **kwargs):
        """
        Validate the data in order to create the object.
        """
        logger.info('Message.create')

        # check if the user is logged in
        if request.user.is_authenticated:
            get_object_or_404(Author, id=request.user.id)
            return super().create(request, *args, **kwargs)
        else:
            raise ValueError("No user is logged in")

    def perform_create(self, serializer):
        """
        Perform the object creation.
        """
        logger.info('Message.perform_create')

        # Add the author and the publication date
        serializer.save(author=self.request.user, publication_date=datetime.datetime.now())
        logger.info('New message saved')
        # Notify tornado
        r = requests.post('http://localhost:1234/message_update', data={'event': 'create'})
        logger.info('Tornado notified: %s' % r.status_code)

    def list(self, request, *args, **kwargs):
        """
        Return the list all of messages. Diff with get_queryset ?
        """
        logger.info('Message.list')

        # get the message list or a text when no one are available
        message_list = super().list(request, *args, **kwargs)
        if len(message_list.data) == 0:
            # Translators: Text displayed on index.html when there are no messages
            return Response(gettext('No messages are available.'))
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
        logger.info('Message.perform_destroy')

        # check if the user is logged in
        if self.request.user.is_authenticated:
            # check if this is the author or an admin
            author = get_object_or_404(Author, id=self.request.user.id)
            if author.id == instance.author.id or author.is_staff:
                # delete the message
                super().perform_destroy(instance)
                # Notify tornado
                r = requests.post('http://localhost:1234/message_update', data={'event': 'delete'})
                logger.info('Tornado notified: %s' % r.status_code)
            else:
                raise ValueError("The logged user is not an admin or the author")
        else:
            raise ValueError("No user is logged in")


class RestAuthorView(viewsets.ModelViewSet):
    """
    REST API author view.
    """

    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
