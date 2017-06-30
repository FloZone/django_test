from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from . import views

# Create a router to automatically create REST urls
router = DefaultRouter()
router.register(r'message', views.RestMessageView)
router.register(r'user', views.RestUserView)

app_name = "firstapp"
urlpatterns = [
    # Views
    url(r'^$', views.IndexView.as_view(), name='index'),  # index page
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),  # detail page

    # Log user
    url(r'^logout$', views.logout_user, name='logout'),
    url('', include('social_django.urls', namespace='social')),

    # REST framework
    url(r'^rest/', include(router.urls, namespace='rest')),
]
