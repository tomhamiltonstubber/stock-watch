from django.urls import path

from StockWatch.main import views

urlpatterns = [
    path('stock-details/', views.stock_details, name='stock-details'),
]
