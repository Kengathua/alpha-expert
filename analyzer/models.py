import uuid
from django.db import models
from django.db.models.deletion import PROTECT

# Create your models here.


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
    date = models.DateTimeField(db_index=True)
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    adj_close = models.FloatField()
    volume = models.CharField(max_length=250)

    def __str__(self):
        return '{}'.format(self.ticker.name)


class Results(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False,
                          unique=True, primary_key=True)
    date = models.DateTimeField(db_index=True)
    ticker = models.CharField(max_length=250)
    today_date = models.CharField(max_length=250, null=True)
    today_price = models.CharField(max_length=250, null=True)
    output_data = models.TextField()
    predicted_price = models.CharField(max_length=250, null=True)
    actual_price = models.CharField(max_length=250, null=True)
    signal = models.CharField(max_length=250)
    # start_date = models.CharField(max_length=250)
    # end_date = models.CharField(max_length=250)
    # user

    def __str__(self):
        return '{}'.format(self.signal)
