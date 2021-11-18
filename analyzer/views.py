import logging

import uuid

import pytz
import datetime

# Create your views here.
import pandas as pd
import numpy as np

from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler

from django.http import HttpResponse, response
from django.core.exceptions import ObjectDoesNotExist
import base64
from io import BytesIO

from rest_framework import viewsets
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Results, Ticker, Stock
from .serializers import TickerSerializer, StockSerializer, ResultsSerializer, CreateResultSerializer

from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler(feature_range=(0, 1))

LOGGER = logging.getLogger(__name__)


class TickerViewSet(viewsets.ModelViewSet):
    queryset = Ticker.objects.all().order_by('name')
    serializer_class = TickerSerializer


class StockViewSet(viewsets.ModelViewSet):
    # queryset = Stock.objects.all().order_by('ticker')
    queryset = Stock.objects.all()
    serializer_class = StockSerializer


class StockView(generics.ListAPIView):
    queryset = Stock.objects.all().order_by('date')
    serializer_class = StockSerializer


class ResultsViewSet(viewsets.ModelViewSet):
    queryset = Results.objects.all().order_by('date')
    serializer_class = ResultsSerializer


class ResultView(generics.ListAPIView):
    queryset = Results.objects.all().order_by('date')
    serializer_class = ResultsSerializer


def load_df(ticker):
    result = []
    try:
        df = pd.read_csv('nse_dfs/{}.csv'.format(ticker), parse_dates=True)
        result = df

    except FileNotFoundError as e:
        msg = "The Ticker {} does not exist".format(ticker)
        msg += "and returned a {} error".format(e)
        LOGGER.error(msg)

    return result


def final_stock_anallyzer(ticker, duration):
    print("Predicting:",ticker)
    look_back = 200
    n_steps = 200
    today_date = '2019-06-30'
    lst_output = []

    df = load_df(ticker)
    df = df.sort_values(by='Date', ascending=1).reset_index(drop=True)
    df1 = df.reset_index()['Close']
    df1 = scaler.fit_transform(np.array(df1).reshape(-1, 1))

    # For deployment
    # Splitting the dataset into train and test data
    past_size = df.loc[df['Date'] == today_date].index[0]
    validation_size = len(df1)-past_size
    past_data, validation_data = df1[0:past_size, :], df1[past_size:len(df1), :1]

    today_price = df.iloc[past_size]['Close']
    actual_price = df.iloc[past_size+duration]['Close']

    model = load_model(
        'trained_models/nse_stock_price_prediction_model_13.h5')

    length_of_past_data = len(past_data)
    x_input_length = length_of_past_data - look_back
    x_input = past_data[x_input_length:].reshape(1, -1)
    print(x_input.shape)
    temp_input = list(x_input)
    temp_input = temp_input[0].tolist()

    i = 0
    while(i < duration):
        if(len(temp_input) > look_back):
            #print(temp_input)
            x_input = np.array(temp_input[1:])
            # print("{} day input {}".format(i,x_input))
            # print('{} day past 100 days scaled input'.format(i),x_input)
            x_input = x_input.reshape(1, -1)
            print('{} day past 100 days input {}'.format(
                i, scaler.inverse_transform(x_input)))
            x_input = x_input.reshape((1, n_steps, 1))
            # print(x_input)
            yhat = model.predict(x_input, verbose=0)
            print("{} day output {} scaler of {}".format(
                i, yhat, scaler.inverse_transform(yhat)))
            temp_input.extend(yhat[0].tolist())
            temp_input = temp_input[1:]
            #print(temp_input)
            lst_output.extend(yhat.tolist())
            i = i+1
        else:
            x_input = x_input.reshape((1, n_steps, 1))
            yhat = model.predict(x_input, verbose=0)
            print(yhat[0])
            temp_input.extend(yhat[0].tolist())
            print(len(temp_input))
            lst_output.extend(yhat.tolist())
            i = i+1

    # print(lst_output)
    predicted_results = scaler.inverse_transform(lst_output).tolist()

    results = []
    for result in predicted_results:
        results.append(result[0])

    return today_date, today_price, results, actual_price

def save_stocks_data_to_db():
    tickers = ['ABSA', 'COOP', 'EQTY', 'HFCK',
               'IMH', 'KCB', 'NBK', 'NCBA', 'SBIC', 'SCBK']

    for ticker in tickers:
        try:
            stock_object = Ticker.objects.get(name=ticker)
            stock_name = str(stock_object)
            msg = "found {}".format((ticker))
            print(msg)

        except Ticker.DoesNotExist:
            msg = "{} ticker not found".format((ticker))
            print(msg)
            model = Ticker(name=ticker)
            model.save()

    for ticker in tickers:
        df = load_df(ticker)
        df.reset_index(inplace=True)
        for index, row in df.iterrows():
            date = row[0]
            start = row[1]
            low = row[2]
            high = row[3]
            close = row[4]
            adj_close = row[5]
            volume = row[6]

            stock_object = Ticker.objects.get(name=ticker)
            stock_name = str(stock_object)
            print(type(stock_name), type(ticker))

            if stock_name == ticker:
                model = Stock(
                    ticker=stock_object, date=date, open=start, high=high,
                    low=low, close=close, adj_close=adj_close, volume=volume
                )
                model.save()
                msg = "Saving {}'s data for {}".format(ticker, date)
                LOGGER.info(msg)
                print(msg)

            else:
                msg = 'The ticker {}'.format(
                    stock_name), 'is not the same as {}'.format(ticker)
                LOGGER.info(msg)
                print(msg)


def compute_advice(current_price, predicted_price):
    advice = ''
    if current_price > predicted_price:
        if predicted_price <= 0.9*current_price:
            msg = "STRONG SELL since the price is predicted to drop significantly"
            advice = msg
        else:
            msg = "WEAK SELL since the price is predicted to drop slightly"
            advice = msg

    elif current_price < predicted_price:
        if predicted_price >= 1.1*current_price:
            msg = "STRONG BUY since the price is predicted to rise significantly"
            advice = msg
        else:
            msg = "WEAK BUY since the price is predicted to rise slightly"
            advice = msg

    else:
        msg = "HOLD since the price is predicted to stay the same"
        advice = msg

    print(msg)
    return advice

class CreateResultView(APIView):
    serializer_class = CreateResultSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        duration = 30
        today_date = '2019-06-30'
        if serializer.is_valid():
            date = str(datetime.datetime.now(pytz.timezone('Africa/Nairobi')))
            ticker = serializer.data.get('ticker')

            if serializer.initial_data.get('duration'):
                duration = int(serializer.initial_data.get('duration'))
                msg = "Includes Duration"
            else:
                msg = "No duration"
                pass

            if serializer.initial_data.get('selected_date'):
                selected_date = serializer.initial_data.get('selected_date')
                msg = "Includes a Selected Date"
                selected_date = datetime.datetime.strptime(selected_date, "%Y-%m-%d")
                today_date = datetime.datetime.strptime(today_date, "%Y-%m-%d")
                delta_difference = selected_date - today_date
                duration = delta_difference.days
            else:
                msg = "No Selected Date"
                pass

            if serializer.initial_data.get('duration') and serializer.initial_data.get('selected_date'):
                selected_date = serializer.initial_data.get('selected_date')
                msg = "Will predict by Selected Date"
                selected_date = datetime.datetime.strptime(
                    selected_date, "%Y-%m-%d")
                today_date = datetime.datetime.strptime(today_date, "%Y-%m-%d")
                delta_difference = selected_date - today_date
                duration = delta_difference.days
            else:
                pass

            msg = "Will be analyzing {}".format(ticker)
            today_date, today_price, results, actual_price = final_stock_anallyzer(
                ticker, duration)
            # today_date = datetime.datetime.strptime(today_date, "%Y-%m-%d").strftime("%Y-%m-%d %H:%M:%S.%f")
            future_day = len(results) - 1
            predicted_price = round(results[future_day], 2)
            output_data = results

            advice = compute_advice(today_price, predicted_price)

            serializer_context = {
                'request': request,
            }

            result = Results(
                id=uuid.uuid4(), date=date, ticker=ticker, output_data=output_data, signal=advice,
                today_date=today_date, today_price=today_price, predicted_price=predicted_price, actual_price=actual_price
            )
            result.save()

        return Response(ResultsSerializer(result, context=serializer_context).data, status=status.HTTP_201_CREATED)
