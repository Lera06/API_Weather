from django.db import models


class City(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'cities'       # It's for admin: Cities not Citys!
