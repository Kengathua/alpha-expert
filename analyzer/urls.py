from rest_framework import routers
from django.urls import path,include
from . import views

router = routers.DefaultRouter()
router.register(r'Tickers', views.TickerViewSet)
router.register(r'Stocks', views.StockViewSet)
router.register(r'Results', views.ResultsViewSet)


urlpatterns = [
    # path('results', views.stock_analyzer, name='results'),
    path('api', include(router.urls)),
    path('stocks', views.StockView.as_view()),
    path('results', views.ResultView.as_view()),
    path('create-result', views.CreateResultView.as_view()),
    # path('', views.load_stock, name='')
]

urlpatterns += router.urls
