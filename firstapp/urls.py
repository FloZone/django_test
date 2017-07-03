from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from . import views


# App namespace
app_name = "firstapp"


# Create a router to automatically create REST urls
router = DefaultRouter()
router.register(r'message', views.RestMessageView)
router.register(r'author', views.RestAuthorView)


urlpatterns = [
    # Views
    url(r'^$', views.index, name='index'),  # index page
    url(r'^message/(?P<message_id>[0-9]+)/$', views.message_detail, name='message-detail'),  # message detail page
    url(r'^author/(?P<author_id>[0-9]+)/$', views.author_detail, name='author-detail'),  # author detail page

    # User logging
    url(r'^logout$', views.logout_user, name='logout'),
    url('', include('social_django.urls', namespace='social')),

    # REST framework
    url(r'^rest/', include(router.urls, namespace='rest')),
    url(r'^rest/', router.get_api_root_view(), name="rest"),

]
