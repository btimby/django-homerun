from django.conf.urls import patterns
from django.conf.urls import include
from django.conf.urls import url

from main.views import IVRMainMenuView


urlpatterns = patterns('',
    url(r'^ivr/(\w+)/$', IVRMainMenuView.as_view(), name='ivr_main')
)
