from django.contrib import admin
from django.db import models

Fave = models.get_model('faves', 'fave')
FaveType = models.get_model('faves', 'favetype')

admin.site.register(Fave)
admin.site.register(FaveType)