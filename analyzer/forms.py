from django import forms
from django.db.models import fields
from django.db.models.base import Model
from .models import *
from stocks.models import Ticker

tickers = Ticker.objects.all()
TICKERS = []

for ticker in tickers:
    TICKER = ticker
    TICKERS.append(TICKER,TICKER)

class VehicleForm(forms.ModelForm):
    ticker = forms.CharField(label='Select the stock you want to predict the price movement', widget=forms.Select(choices=TICKERS))
    fig = forms.ImageField()
