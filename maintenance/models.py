from __future__ import unicode_literals
from django.db import models


# Create your models here.
class VM(models.Model):
	ip = models.CharField(max_length=45, null=False, default="127.0.0.1")
	host = models.CharField(max_length=25, null=False, default='redhat66')
	username = models.CharField(max_length=25, null=False, default='root')
	passward = models.CharField(max_length=25, null=False, default='rootroot')

	def __str__(self):
		return self.ip
