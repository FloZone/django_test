from django.conf.urls import url, include

from . import views

app_name = "firstapp"
urlpatterns = [
    # Views
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),

    # Delete
    url(r'^message/delete/$', views.delete_message, name='delete_message'),
    url(r'^answer/delete/$', views.delete_answer, name='delete_answer'),

    # Create
    url(r'^post/$', views.post, name='post'),
    url(r'^(?P<message_id>[0-9]+)/answer/$', views.answer, name='answer'),

    # Get
    url(r'^get_message/$', views.get_message, name='get_message'),
    url(r'^(?P<message_id>[0-9]+)/get_answer/$', views.get_answer, name='get_answer'),

    # Log user
    url(r'^logout$', views.logout_user, name='logout'),
    url('', include('social_django.urls', namespace='social')),
]
