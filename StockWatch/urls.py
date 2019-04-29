from django.urls import path

from StockWatch.main import views

urlpatterns = [
    path('search/symbols/', views.search_company_symbols, name='symbol-search'),
    path('search/', views.search, name='search'),
]
