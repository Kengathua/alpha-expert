import uuid

from django.db import models

from django.utils import timezone
from django.db.models.deletion import PROTECT


""" The model for storing collected data """
class Ticker(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False,
                          unique=True, primary_key=True)
    name = models.CharField(max_length=250)

    def __str__(self):
        return "%s" % (self.name)


class Stock(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False,
                          unique=True, primary_key=True)
    ticker = models.ForeignKey(
        Ticker, related_name="ticker_name", max_length=250, on_delete=PROTECT)
    date = models.DateTimeField(db_index=True, default=timezone.now)
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    adj_close = models.FloatField()
    volume = models.CharField(max_length=250)

    def __str__(self):
        return '{}'.format(self.ticker.name)
