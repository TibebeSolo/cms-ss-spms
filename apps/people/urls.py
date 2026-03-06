from django.urls import path
from . import views

app_name = 'people'
urlpatterns = [
    # HTMX datepicker form path
    path('hx/convert-date/', views.hx_convert_eth_date, name='hx-convert-eth-date'),

    # Placeholder for the Christian Search/List
   # path('list/', views.ChristianListView.as_view(), name='christian-list'),
]