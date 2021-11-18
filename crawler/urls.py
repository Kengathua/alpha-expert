#========================================= DRF (REST urls)=========================================
from django.urls import include, path
from rest_framework import routers
from . import views
from django_filters.rest_framework import DjangoFilterBackend


router = routers.DefaultRouter()
router.register(r'Tickers', views.TickerViewSet)
router.register(r'Stocks', views.StockViewSet)

urlpatterns =[
    path('crawler/', views.crawler, name='crawler')
]


