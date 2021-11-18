"""
Getting the NYSE fortune 500 companies data
Aims at using this readily available stock data to train the models
"""
import os
import pytz
import csv
import time
import pickle
import logging
import calendar
import requests
import datetime
import datetime


from datetime import date
from functools import wraps
from bs4 import BeautifulSoup
from selenium import webdriver
from collections import Counter
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from pandas_datareader._utils import RemoteDataError
from selenium.webdriver.chrome.options import Options

import bs4 as bs
import numpy as np
import pandas as pd
import mplfinance as mpf
import pandas_datareader.data as web

from sklearn.neighbors import KNeighborsClassifier
from sklearn import svm, model_selection, neighbors
from sklearn.ensemble import VotingClassifier, RandomForestClassifier

from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from .serializers import *
from .models import Ticker, Stock
from .forms import StockForm


class TickerViewSet(viewsets.ModelViewSet):
    queryset = Ticker.objects.all().order_by('name')
    serializer_class = TickerSerializer


class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all().order_by('ticker')
    serializer_class = StockSerializer

# ==================================== The NSE crawler function ==================================


def nse_crawler(request):
    URL = "https://afx.kwayisi.org/nse/"
    page = requests.get(URL)

    def access_axf():
        options = Options()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--incognito')
        options.add_argument('--headless')
        driver = webdriver.Chrome(
            "/usr/bin/chromedriver", options=options)
        driver.get("https://afx.kwayisi.org/nse/")

        page_source = driver.page_source

        soup = BeautifulSoup(page_source, 'lxml')

        return soup

    access_axf()

    def tableDataText():
        """Parses a html segment started with tag <table> followed 
        by multiple <tr> (table rows) and inner <td> (table data) tags. 
        It returns a list of rows with inner columns. 
        Accepts only one <th> (table header/data) in the first row.
        """
        soup = access_axf()

        def rowgetDataText(tr, coltag='td'):  # td (data) or th (header)
            return [td.get_text(strip=True) for td in tr.find_all(coltag)]

        current = []
        trs = soup.find('div', class_='t').find_all('tr')
        headerow = rowgetDataText(trs[0], 'th')
        if headerow:  # if there is a header row include first
            current.append(headerow)
            trs = trs[1:]

        for tr in trs:  # for every table row
            current.append(rowgetDataText(tr, 'td'))  # data row

        return current

    # tableDataText()

    def list_nse_tickers():
        """ Returns a list of all tickers """
        tickers = []
        stocks = tableDataText()
        for stock in stocks[1:]:
            ticker = stock[0]
            tickers.append(ticker)

        with open("list_current_tickers.pickle", "wb") as f:
            pickle.dump(ticker, f)

        return tickers

    list_nse_tickers()

    def save_tickers_to_db():
        tickers = list_nse_tickers()

        for ticker in tickers:
            try:
                Ticker.objects.get(name=ticker)
                pass

            except Ticker.DoesNotExist:
                model = Ticker(name=ticker)
                model.save()

    save_tickers_to_db()

    def get_latest_record_for_each_ticker():
        tickers = Ticker.objects.all()
        all_latest_data = []

        for ticker in tickers:
            latest_data = list(Stock.objects.filter(ticker=ticker).values_list(
                'ticker', 'date', 'open', 'low', 'high')[:1])
            all_latest_data.append(latest_data)

        return all_latest_data

    # get_latest_record_for_each_ticker()

    def get_current_data():
        if not os.path.exists('nse_dfs'):
            os.makedirs('nse_dfs')

        date = str(datetime.datetime.now(pytz.timezone('Africa/Nairobi')))
        now = datetime.datetime.now(pytz.timezone('Africa/Nairobi'))
        current_time = now.strftime("%H:%M:%S")

        latest_stock_data = get_latest_record_for_each_ticker()
        for i in range(0, len(latest_stock_data)):
            try:
                ticker_id = latest_stock_data[i][0][0]
                latest_date = latest_stock_data[i][0][1]
                latest_open = latest_stock_data[i][0][2]
                latest_low = latest_stock_data[i][0][3]
                latest_high = latest_stock_data[i][0][4]

            except IndexError:
                ticker_id = ''
                latest_date = ''
                latest_open = ''
                latest_high = ''
                latest_low = ''

        if latest_date == '':  # if the there is no record
            start = 0
            current_low = 0
            current_high = 0

        if latest_date == date:  # if the date is today
            start = latest_open
            current_low = latest_low
            current_high = latest_high
        else:
            start = 0  # Set open price to be 0
            current_low = 0   # Set low price to be 0
            current_high = 0  # Set high price to be 0

        market_opening_time = now.replace(
            hour=9, minute=00, second=0, microsecond=0)
        market_closing_time = now.replace(
            hour=17, minute=00, second=0, microsecond=0)

        if now > market_opening_time and now < market_closing_time:
            msg = "Open"
        elif now == market_opening_time:
            msg = "Opening"
        elif now == market_closing_time:
            msg = "Closing"
        else:
            msg = "Closed"

        all_current_data = tableDataText()

        fieldnames = ['Date', 'Open', 'High',
                      'Low', 'Close', 'Adj Close', 'Volume']

        for current_data in all_current_data[1:]:
            ticker = current_data[0]
            volume = current_data[2]

            """Reference tickers table from db to get the name of the tickers to be added to the database"""
            field_name = 'name'
            stock_obj = Ticker.objects.get(name=ticker)
            stock_name = getattr(stock_obj, field_name)

            try:
                current = float(current_data[3])
            except ValueError:
                current = float(current_data[3].replace(',', ""))

            if start == 0:  # if the open price is 0
                start = current
            else:
                start = start

            if current >= current_high:
                high = current
            else:
                high = current_high

            current_low = start
            if current <= current_low:
                low = current
            else:
                low = current_low

            rows = [{
                'Date': date,
                'Open': start,
                'High': high,
                'Low': low,
                'Close': current,
                'Adj Close': current,
                'Volume': volume,
            }]

            if stock_name == ticker:
                model = Stock(
                    ticker=stock_obj, date=date, open=start, high=high,
                    low=low, close=current, adj_close=current, volume=volume
                )
                model.save()
                print("Saved")
            else:
                msg = 'The ticker {}'.format(
                    stock_name), 'is not the same as {}'.format(ticker)
                print(msg)

            if not os.path.exists("nse_dfs/{}.csv".format(ticker)):
                try:
                    with open('nse_dfs/{}.csv'.format(ticker), "w", encoding='UTF8', newline='') as f:
                        csv_writer = csv.DictWriter(
                            f, fieldnames=fieldnames)
                        csv_writer.writeheader()
                        csv_writer.writerows(rows)
                except RemoteDataError as exp:
                    print('Unable to read data from: {}'.format(ticker))
            else:
                try:
                    with open('nse_dfs/{}.csv'.format(ticker), "a", encoding='UTF8', newline='') as f:
                        csv_writer = csv.DictWriter(
                            f, fieldnames=fieldnames)
                        csv_writer.writerows(rows)
                except RemoteDataError as exp:
                    print('Unable to read data from: {}'.format(ticker))

    # get_current_data()

    def automate_data_collection():
        now = datetime.datetime.now(pytz.timezone('Africa/Nairobi')).time()
        market_opening_time = now.replace(
            hour=9, minute=00, second=0, microsecond=0)
        market_closing_time = now.replace(
            hour=17, minute=00, second=0, microsecond=0)

        """ Data collection will happen between MONDAY[0] and FRIDAY[4].  """
        crawling_day = False
        crawling_time = False
        status = "Offline"
        today_id = date.today().weekday()
        day_name = calendar.day_name[today_id]

        if today_id >= 0 and today_id <= 4:
            msg = "Today is {}".format(day_name)
            print(msg)
            crawling_day = True

        if now > market_opening_time and now < market_closing_time:
            msg = "Running at {}".format(now)
            print(msg)
            crawling_time = True

        if crawling_day and crawling_time:
            status = "Online"

        print(status)

        """ Data collection will happen between Opening time 9.00 am and Closing time 5.00pm.  """
        while crawling_day and crawling_time:
            get_current_data()

        # while now > market_opening_time:
        #     print("running past crawling time")
        #     get_current_data()
        
        # while now < market_opening_time:
        #     print("running before crawling time")
        #     get_current_data()
        return status

    automate_data_collection()

    now = datetime.datetime.now(pytz.timezone(
        'Africa/Nairobi')).time().strftime('%H:%M:%S')
    c_date = datetime.datetime.now(pytz.timezone(
        'Africa/Nairobi')).date().strftime('%Y-%m-%d')
    status = automate_data_collection()

    html = "<html><body>The system is {}".format(status), " as at {} ".format(
        now), "on {}.</body></html>".format(c_date)
    return HttpResponse(html)
