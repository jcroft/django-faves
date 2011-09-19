import datetime

from django.http import Http404, HttpResponse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import models

Fave = models.get_model('faves', 'fave')
FaveType = models.get_model('faves', 'favetype')

def user_faves(request, username, fave_type_slug, template_name='faves/user_faves.html'):
  """
  Displays all the faves of a given type for the given user.
  """
  user = get_object_or_404(User, username=username)
  fave_type = get_object_or_404(FaveType, slug=fave_type_slug)
  faves = Fave.objects.get_for_user(user, fave_type)
  return render_to_response(template_name, RequestContext(request, { 'fave_user': user, 'fave_type': fave_type, 'faves': faves }))

@login_required
def toggle_fave_ajax(request, content_type_id, object_id, fave_type_slug):
  """ View that toggles the status of a favorite, for AJAX requests. """
  if request.is_ajax():
    content_type  = get_object_or_404(ContentType, id=content_type_id)
    faved_object  = get_object_or_404(content_type.model_class(), pk=object_id)
    fave_type     = FaveType.objects.get(slug=fave_type_slug)
    fave, created = Fave.objects.get_or_create(type=fave_type, user=request.user, content_type=content_type, object_id=faved_object.id)
    if not created:
      if fave.withdrawn: fave.withdrawn = False
      else: fave.withdrawn = True
      fave.save()
    context = "{'success': 'true', 'content_object_id': '%s'}" % (faved_object.id)
    return HttpResponse(context, mimetype="application/json")
  else:
    raise Http404("This view only works with AJAX requests.")

@login_required
def fave_object(request, content_type_id, object_id, fave_type_slug, success_template_name='faves/fave_done.html'):
  """
  Adds a "fave" relationship from a user to any object, and then returns a success page.
  """
  content_type  = get_object_or_404(ContentType, id=content_type_id)
  faved_object  = get_object_or_404(content_type.model_class(), pk=object_id)
  fave_type     = FaveType.objects.get(slug=fave_type_slug)
  fave          = Fave.objects.create_or_update(request.user, faved_object, fave_type, force_not_withdrawn=True)
  if request.is_ajax():
    context = "{'success': 'true', 'content_object_id': '%s'}" % (faved_object.id)
    return HttpResponse(context, mimetype="application/json")
  else:
    return render_to_response(success_template_name, RequestContext(request, { 'fave': fave }))

      
@login_required
def unfave_object(request, content_type_id, object_id, fave_type_slug, success_template_name='faves/unfave_done.html'):
  """
  Removes a "fave" relationship from a user to an object, and then returns a success page.
  """
  content_type  = get_object_or_404(ContentType, id=content_type_id)
  faved_object  = get_object_or_404(content_type.model_class(), pk=object_id)
  fave_type     = FaveType.objects.get(slug=fave_type_slug)
  fave          = Fave.objects.withdrawl(request.user, faved_object, fave_type)
  if request.is_ajax():
    context = "{'success': 'true', 'content_object_id': '%s'}" % (faved_object.id)
    return HttpResponse(context, mimetype="application/json")
  else:
    return render_to_response(success_template_name, RequestContext(request, { 'fave': fave }))
