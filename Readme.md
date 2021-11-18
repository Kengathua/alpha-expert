_Backend-Pyhton Django_
Frontend - Basic Html, css, js

ML-Python, deep learning keras module under tensorflow
streamlit to run the models.(Local development server with a simple UI for implementing models)

Terms
Ticker = Abbreaviation of a stock used to represent a stock

The crawler:
It scraps data from afx.kwayisi.org site which contains realtime data for most africa stocks
It used selenium to gain access to the site since it is a dynamic site written in angularjs
beautifulsoup is used to parse over the records to obtain the values for the different stocks

Starts working at 9:00 am to 5:00 for the specified period.
It records the start price, close price , highest price (by comparing the current price with the last recorded high),
lowest price (by comparing the current price with the last recorded low) and the volume of stocks sold.
