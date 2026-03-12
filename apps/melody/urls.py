from django.urls import path
from . import views

app_name = 'melody'

urlpatterns = [
    # mock paths 
    path('mezemran/', views.mezemran_list, name='mezemran-list'),
    path('mezemran/roster/', views.mezemran_roster, name='roster')
    
]