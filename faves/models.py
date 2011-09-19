import datetime

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.conf import settings

from faves.managers import FaveManager, WithdrawnFaveManager, NonWithdrawnFaveManager

class FaveType(models.Model):
  """
  A FaveType is a "type" of relationship between a user and an object. This
  allows you to use one app (django-faves) for multiple types of 
  relationships. For example, perhaps you want to let users "favorite" 
  objects, but also add them to a "wishlist". Or to "flag" them as offensive.
  By creating multiple FaveType instances, you can do this sort of thing.
  
  """
  name = models.CharField(max_length=255, help_text="The singular name of this fave type, i.e. 'Favorite' or 'Wishlist Item'.")
  slug = models.SlugField()

  def __unicode__(self):
    return self.name

class Fave(models.Model):
  """
  A Fave is a relationship between a user and an object in the database.
  """
  type                            = models.ForeignKey(FaveType, related_name="faves", default=1)
  content_type                    = models.ForeignKey(ContentType, related_name="faves")
  object_id                       = models.IntegerField()
  content_object                  = generic.GenericForeignKey()
  user                            = models.ForeignKey(User, related_name="faves")
  withdrawn                       = models.BooleanField(default=False)
  date_created                    = models.DateTimeField(default=datetime.datetime.now)
  date_updated                    = models.DateTimeField(blank=True, null=True)
  objects                         = FaveManager()
  withdrawn_objects               = WithdrawnFaveManager()
  active_objects                  = NonWithdrawnFaveManager()
  
  def __unicode__(self):
    return "[%s] %s, %s" % (self.type.name, self.user.username, self.content_object)
  
  def save(self, force_insert=False, force_update=False):
    self.date_updated = datetime.datetime.now()
    super(Fave, self).save(force_insert=force_insert, force_update=force_update)