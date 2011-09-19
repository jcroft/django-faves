from django.conf.urls.defaults import *

from faves.views import *

urlpatterns = patterns('', 
  url(
    regex   = r'^(?P<fave_type_slug>[-\w]+)/(?P<content_type_id>\d+)/(?P<object_id>\d+)/$',
    view    = fave_object,
    name    = 'fave_object',
  ),
  url(
    regex   = r'^remove/(?P<fave_type_slug>[-\w]+)/(?P<content_type_id>\d+)/(?P<object_id>\d+)/$',
    view    = unfave_object,
    name    = 'unfave_object',
  ),
  url(
    regex   = r'^users/(?P<username>[-\w]+)/(?P<fave_type_slug>[-\w]+)/$',
    view    = user_faves,
    name    = 'user_faves',
  ),
  url(
    regex   = r'^toggle/(?P<fave_type_slug>[-\w]+)/(?P<content_type_id>\d+)/(?P<object_id>\d+)/$',
    view    = toggle_fave_ajax,
    name    = 'toggle_fave',
  ),
)