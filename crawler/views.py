from django.shortcuts import render

# Create your views here.
import os
import datetime
from datetime import date
import requests
from bs4 import BeautifulSoup

import datetime
from datetime import date
import requests
from bs4 import BeautifulSoup

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

from pandas_datareader._utils import RemoteDataError

import csv
from django.http import HttpResponse
from rest_framework import viewsets

from .models import Ticker, Stock
from .serializers import TickerSerializer, StockSerializer

options = Options()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')

driver = webdriver.Chrome(
    "/usr/bin/chromedriver", options=options)


class TickerViewSet(viewsets.ModelViewSet):
    queryset = Ticker.objects.all().order_by('name')
    serializer_class = TickerSerializer


class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all().order_by('ticker')
    serializer_class = StockSerializer

def crawler(request):
    base = datetime.datetime.today().date()
    date_list = [base - datetime.timedelta(days=x) for x in range(5)]
    stocks = []

    def save_tickers():
        tickers=[]
        for i in range(3, 88):
            try:
                ticker_xpath = '//*[@id="pricelist"]/tbody/tr[{}]/td[1]'.format(i)
                ticker = driver.find_element_by_xpath(ticker_xpath).text
                tickers.append(ticker)
            
            except NoSuchElementException:
                pass

        for ticker in tickers:
            try:
                Ticker.objects.get(name=ticker)
                pass

            except Ticker.DoesNotExist:
                model = Ticker(name=ticker)
                model.save()

    save_tickers()

    def get_historical_data():
        if not os.path.exists('historical_nse_dfs'):
            os.makedirs('historical_nse_dfs')

        for date in date_list:
            date = str(date)
            asin = str(date).replace('-', '')
            url = 'https://live.mystocks.co.ke/price_list/{}'.format(asin)

            driver.get(url)

            for i in range(3, 88):
                try:
                    sector_xpath = '//*[@id="pricelist"]/tbody/tr[{}]'.format(i)
                    ticker_xpath = '//*[@id="pricelist"]/tbody/tr[{}]/td[1]'.format(i)
                    company_xpath = '//*[@id="pricelist"]/tbody/tr[{}]/td[2]/a'.format(
                        i)
                    low_xpath = '//*[@id="pricelist"]/tbody/tr[{}]/td[5]'.format(i)
                    high_xpath = '//*[@id="pricelist"]/tbody/tr[{}]/td[6]'.format(i)
                    current_xpath = '//*[@id="pricelist"]/tbody/tr[{}]/td[7]'.format(i)
                    open_xpath = '//*[@id="pricelist"]/tbody/tr[{}]/td[8]'.format(i)
                    volume_xpath = '//*[@id="pricelist"]/tbody/tr[{}]/td[12]'.format(i)

                    stock = []
                    stock.append(date)
                    sector = driver.find_element_by_xpath(sector_xpath).text
                    stock.append(sector)
                    ticker = driver.find_element_by_xpath(ticker_xpath).text
                    stock.append(ticker)
                    company = driver.find_element_by_xpath(company_xpath).text
                    stock.append(company)
                    low = driver.find_element_by_xpath(low_xpath).text
                    stock.append(low)
                    high = driver.find_element_by_xpath(high_xpath).text
                    stock.append(high)
                    current = driver.find_element_by_xpath(current_xpath).text
                    stock.append(current)
                    open = driver.find_element_by_xpath(open_xpath).text
                    stock.append(open)
                    volume = driver.find_element_by_xpath(volume_xpath).text
                    stock.append(volume)

                    stocks.append(stock)

                except NoSuchElementException:
                    pass
            
        return stocks
    
    def save_historical_data():

        stocks= get_historical_data()

        fieldnames = ['Date', 'Open', 'Low', 'High', 'Close', 'Adj Close', 'Volume']

        for stock in stocks:
            ticker = stock[2]
            date = stock[0]
            low = (stock[4])
            high = (stock[5])
            close = (stock[6])
            open = (stock[7])
            volume = (stock[8])

            print(date, ticker, low, high, close, open, volume)

            rows = [{
                    'Date': date,
                    'Open': open,
                    'Low': low,
                    'High': high,
                    'Close': close,
                    'Adj Close': close,
                    'Volume': volume,
                    }]
            
            # field_name = 'name'
            # stock_obj = Ticker.objects.get(name=ticker)
            # stock_name = getattr(stock_obj, field_name)

            if os.path.exists("historical_nse_dfs/{}.csv".format(ticker)):
                print(type(ticker))
                with open('historical_nse_dfs/{}.csv'.format(ticker), "a", encoding='UTF8', newline='') as f:
                    print('Appending')
            
            html = "<html><body>Getting historical Data</body></html>"
        return HttpResponse(html)

    save_historical_data()
