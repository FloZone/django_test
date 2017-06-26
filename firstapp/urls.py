from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from . import views

# Create a router to automatically create re
router = DefaultRouter()
router.register(r'message', views.RestMessageView)
router.register(r'answer', views.RestAnswerView)
router.register(r'user', views.RestUserView)

app_name = "firstapp"
urlpatterns = [
    # Views
    url(r'^$', views.IndexView.as_view(), name='index'),  # index page
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),  # detail page

    # Log user
    url(r'^logout$', views.logout_user, name='logout'),
    url('', include('social_django.urls', namespace='social')),

    # Delete
    # TODO move to REST API
    url(r'^message/delete/$', views.delete_message, name='delete_message'),
    url(r'^answer/delete/$', views.delete_answer, name='delete_answer'),

    # Create
    # TODO move to REST API
    url(r'^post/$', views.post, name='post'),
    url(r'^(?P<message_id>[0-9]+)/answer/$', views.answer, name='answer'),

    # Get
    # TODO move to REST API
    url(r'^get_message/$', views.get_message, name='get_message'),
    url(r'^(?P<message_id>[0-9]+)/get_answer/$', views.get_answer, name='get_answer'),



    # REST framework
    url(r'^rest/', include(router.urls, namespace='rest')),
]
