import datetime

from django.db import models
from django.contrib.contenttypes.models import ContentType

class NonWithdrawnFaveManager(models.Manager):
  """
  Custom manager for faves which only returns blogs without status 'Withdrawn'.
  """
  def get_query_set(self):
    return super(NonWithdrawnFaveManager, self).get_query_set().filter(withdrawn=False)

class WithdrawnFaveManager(models.Manager):
  """
  Custom manager for faves which only returns blogs with status 'Withdrawn'.
  """
  def get_query_set(self):
    return super(WithdrawnFaveManager, self).get_query_set().filter(withdrawn=True)

class FaveManager(models.Manager):
  def create_or_update(self, user, content_object, fave_type, force_not_withdrawn=False):
    """
    Creates or updates a favorite relationship.
    """
    Fave = models.get_model('faves', 'fave')
    content_type = ContentType.objects.get_for_model(content_object)
    fave, fave_created = Fave.objects.get_or_create(
      type          = fave_type,
      content_type  = content_type, 
      object_id     = content_object.id, 
      user          = user,
      defaults      = dict(
                        date_created  = datetime.datetime.now(),
                        withdrawn     = False,
                      ),
      )
    if force_not_withdrawn:
      fave.withdrawn=False
      fave.save()
    return fave

  def withdrawl(self, user, content_object, fave_type):
    """
    Withdrawls a favorite relationship.
    """
    Fave = models.get_model('faves', 'fave')
    content_type = ContentType.objects.get_for_model(content_object)

    fave = Fave.objects.get(type=fave_type, content_type=content_type, object_id=content_object.id, user=user)
    fave.withdrawn = True
    fave.save()
    return fave
  
  def active(self):
    """
    Returns only faves which are not withdrawn.
    """
    return self.filter(withdrawn=False)
    
  def withdrawn(self):
    """
    Returns only faves which are withdrawn.
    """
    return self.filter(withdrawn=True)
  
  def get_for_user(self, user, fave_type=None):
    """
    Returns all Fave objects for the given user. If a fave_type is provided,
    returns only faves of that type.
    """
    if fave_type:
      return self.filter(withdrawn=False, type=fave_type, user=user)
    else:
      return self.filter(withdrawn=False, user=user)
  
  def get_for_model(self, model, fave_type=None):
    """
    Returns Fave objects saved for a particular model
    (i.e. all faves for photos, all faves for blog entries, etc.)
    """
    content_type = ContentType.objects.get_for_model(model)
    if fave_type:
      return self.filter(type=fave_type, content_type=content_type)
    else:
      return self.filter(content_type=content_type)