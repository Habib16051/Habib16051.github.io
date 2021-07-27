from django.db import models

# Create your models here.
class Snippet(models.Model):
	name = models.CharField(max_length=255)
	content = models.TextField(blank=True)
	
	def __unicode__(self):
		return self.name
		
