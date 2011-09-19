import datetime

from django import template
from django.template import Library, Node
from django.contrib.contenttypes.models import ContentType
from django.template import resolve_variable
from django.core.urlresolvers import reverse
from django.db import models

register = Library()

Fave = models.get_model('faves', 'fave')
FaveType = models.get_model('faves', 'favetype')

@register.simple_tag
def get_toggle_fave_url(object, fave_type_slug='favorite'):
  """
  Given an object, returns the URL for "toggle favorite for this item".
  Optionally takes a second argument, which is the slug of a 
  FaveType object. If this is provided, will return the URL for
  that FaveType. If not, will use the first FaveType (which, by
  default, is "Favorite".)
  
  Example usage:
  
  {% load faves %}
  <p><a href="{% get_toggle_fave_url photo favorite %}">{% if request.user|has_faved:photo %}Unfavorite{% else %}Favorite{% endif %} this photo</a></p>

  """
  try:
    fave_type = FaveType.objects.get(slug=fave_type_slug)
    content_type = ContentType.objects.get(app_label=object._meta.app_label, model=object._meta.module_name)
    return reverse('toggle_fave', args=(fave_type.slug, content_type.id, object.id))
  except:
    return ''


@register.simple_tag
def get_fave_url(object, fave_type_slug='favorite'):
  """
  Given an object, returns the URL for "favorite this item".
  Optionally takes a second argument, which is the slug of a 
  FaveType object. If this is provided, will return the URL for
  that FaveType. If not, will use the first FaveType (which, by
  default, is "Favorite".)
  
  Example usage:
  
  {% load faves %}
  {% if request.user|has_faved:photo %}
    <p><a href="{% get_unfave_url photo favorite %}">Unfavorite this photo</a></p>
  {% else %}
    <p><a href="{% get_fave_url photo favorite %}">Favorite this photo</a></p>
  {% endif %}
  
  """
  try:
    fave_type = FaveType.objects.get(slug=fave_type_slug)
    content_type = ContentType.objects.get(app_label=object._meta.app_label, model=object._meta.module_name)
    return reverse('fave_object', args=(fave_type.slug, content_type.id, object.id))
  except:
    return ''

@register.simple_tag
def get_unfave_url(object, fave_type_slug='favorite'):
  """
  Given an object, returns the URL for "unfavorite this item."
  Optionally takes a second argument, which is the slug of a 
  FaveType object. If this is provided, will return the URL for
  that FaveType. If not, will default to the first FaveType (which,
  by default, is "Favorite".)
  
  Example usage:
  
  {% load faves %}
  {% get_fave by user on photo of type favorite as fave %}
  {% if fave %}
    <p><a href="{% get_unfave_url photo 'favorite' %}">Unfavorite this photo</a></p>
  {% else %}
    <p><a href="{% get_fave_url photo 'favorite' %}">Favorite this photo</a></p>
  {% endif %}
  """
  try:
    fave_type = FaveType.objects.get(slug=fave_type_slug)
    content_type = ContentType.objects.get(app_label=object._meta.app_label, model=object._meta.module_name)
    return reverse('unfave_object', args=(fave_type.slug, content_type.id, object.id))
  except:
    return ''


class GetFavoritesForUserNode(template.Node):
    def __init__(self, user, fave_type_slug, varname):
      self.user, self.fave_type_slug, self.varname = user, fave_type_slug, varname

    def render(self, context):
      try:
        user                  = resolve_variable(self.user, context)
        fave_type             = FaveType.objects.get(slug=self.fave_type_slug)
        context[self.varname] = Fave.objects.active().filter(type=fave_type, user=user)
      except:
        pass
      return ''

@register.tag
def get_faves_for_user(parser, token):
    """
    Retrieves a specific page object by URL and assigns it to a context variable.

    Syntax::

        {% get_faves_for_user [user] of type [fave-type-slug] as [varname] %}

    Example::

        {% get_faves_for_user user of type favorite as faves %}

    """
    bits = token.contents.split()
    if len(bits) != 7:
        raise template.TemplateSyntaxError("'%s' tag takes six arguments" % bits[0])
    if bits[2] != 'of':
        raise template.TemplateSyntaxError("fifth argument to '%s' tag must be 'as'" % bits[0])
    if bits[3] != 'type':
        raise template.TemplateSyntaxError("fifth argument to '%s' tag must be 'as'" % bits[0])
    if bits[5] != 'as':
        raise template.TemplateSyntaxError("fifth argument to '%s' tag must be 'as'" % bits[0])
    return GetFavoritesForUserNode(bits[1], bits[4], bits[6])


class GetFavoriteNode(template.Node):
    def __init__(self, user, object, fave_type_slug, varname):
      self.user, self.object, self.fave_type_slug, self.varname = user, object, fave_type_slug, varname

    def render(self, context):
      try:
        user                  = resolve_variable(self.user, context)
        object                = resolve_variable(self.object, context)
        content_type          = ContentType.objects.get(app_label=object._meta.app_label, model=object._meta.module_name)
        fave_type             = FaveType.objects.get(slug=self.fave_type_slug)
        try:
          fave                = Fave.active_objects.get(type=fave_type, user=user, content_type=content_type, object_id=object.id)
        except:
          fave = None
        context[self.varname] = fave
      except:
        pass
      return ''

@register.tag
def get_fave(parser, token):
    """

    Syntax::

        {% get_fave by [user] on [object] of type [fave-type-slug] as [varname] %}

    Example::

        {% get_fave by user on photo of type favorite as fave %}

    """
    bits = token.contents.split()
    if len(bits) != 10:
        raise template.TemplateSyntaxError("'%s' tag takes nine arguments" % bits[0])
    if bits[1] != 'by':
        raise template.TemplateSyntaxError("first argument to '%s' tag must be 'by'" % bits[0])
    if bits[3] != 'on':
        raise template.TemplateSyntaxError("third argument to '%s' tag must be 'on'" % bits[0])
    if bits[5] != 'of':
        raise template.TemplateSyntaxError("fifth argument to '%s' tag must be 'of'" % bits[0])
    if bits[6] != 'type':
        raise template.TemplateSyntaxError("sixth argument to '%s' tag must be 'type'" % bits[0])
    if bits[8] != 'as':
        raise template.TemplateSyntaxError("eighth argument to '%s' tag must be 'as'" % bits[0])
    return GetFavoriteNode(bits[2], bits[4], bits[7], bits[9])