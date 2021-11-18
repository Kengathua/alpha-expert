#========================================= DRF (REST urls)=========================================
from django.urls import include, path
from rest_framework import routers
from . import views
from django_filters.rest_framework import DjangoFilterBackend


router = routers.DefaultRouter()
router.register(r'Tickers', views.TickerViewSet)
router.register(r'Stocks', views.StockViewSet)

urlpatterns = [
    path('api', include(router.urls)),
    #path('api-auth/', include('rest_framework.urls', namespace='api_rest_framework'))
]


urlpatterns +=[
    # path('form/', views.FormView, name='form'),
    path('live_crawler/', views.nse_crawler, name='live_crawler')
]

