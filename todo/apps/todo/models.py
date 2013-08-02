from django.db import models


class ToDo(models.Model):
    text = models.CharField(max_length=100)
    completed = models.BooleanField(default=False)

    class Meta:
        ordering = ('-id',)
