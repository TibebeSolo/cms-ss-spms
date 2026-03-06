from .views import login_view
from django.urls import path

urlpatterns = [
    path('login/', login_view, name='login'),
]
