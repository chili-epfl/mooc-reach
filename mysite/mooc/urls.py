from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
#from django.contrib.staticfiles.urls import staticfiles_urlpatterns
#import settings

from django.conf import settings
from . import views

urlpatterns = patterns('',
                       url(r'^index/$', views.index, name= 'index'),
                       url(r'^index/results/(?P<keyword>[-\w]+)/(?P<derivative>[-\w]+)$', views.results, name='results'),
                       #url(r'^media/(?P<path>.*)$','django.views.static.serve',{'document_root':settings.MEDIA_ROOT}),
                       )

#urlpatterns += staticfiles_urlpatterns()