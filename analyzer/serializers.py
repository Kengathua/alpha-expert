from numpy import mod
from rest_framework import serializers
from rest_framework.response import Response
from .models import *

from rest_framework.fields import CharField

class StockSerializer(serializers.HyperlinkedModelSerializer):
    ticker = CharField(source='ticker.name', read_only=True)
    class Meta:
        model = Stock
        fields = '__all__'


class TickerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Ticker
        fields = '__all__'


class ResultsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Results
        fields = '__all__'


class CreateResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Results
        fields=['ticker']
