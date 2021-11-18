from django import forms
from .models import Stock


# TICKERS = [
#     ('ABSA', 'ABSA'),
#     ('KCB', 'KCB'),
# ]

TICKERS = [
    ('AFL', 'AFL'),
    ('MMM', 'MMM'),
    ('LNT', 'LNT'),
]

class StockForm(forms.ModelForm):
    ticker = forms.CharField(
        label='Select the stock you want to predict', widget=forms.Select(choices=TICKERS))

    class Meta:
              model = Stock
              fields = ('ticker',)

