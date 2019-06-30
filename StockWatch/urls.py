from django.urls import path
from django.contrib.auth import views as auth_views

from StockWatch.main import views

urlpatterns = [
    path('', views.search, name='search'),
    path('login/', views.login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('search/symbols/', views.search_company_symbols, name='symbol-search'),
]
