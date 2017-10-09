from django.db import models


class Rin(models.Model):
    id = models.AutoField(primary_key=True)
    tree_species = models.CharField(max_length=255, null=False)
    diameter = models.FloatField(null=False)
    jukou = models.FloatField(null=False)
    latitude = models.FloatField(null=False)
    longitude = models.FloatField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
