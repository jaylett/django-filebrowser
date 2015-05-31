from django.conf.urls import patterns, include, url
from django.contrib import admin
from filebrowser.sites import site

urlpatterns = patterns(
    '',
   url(r'^filebrowser/', include(site.urls)),
   url(r'^admin/', include(admin.site.urls)),
)
