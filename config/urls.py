from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

# A simple inline view for the Dashboard to test the layout immediately
@login_required
def dashboard_view(request):
    from django.shortcuts import render
    return render(request, 'layouts/dashboard.html')

urlpatterns = [
    path('admin/', admin.site.urls),

    # The Identity App
    path('identity/', include('identity.urls', namespace='identity')),
    
    # Other Apps
    # path('people/', include('apps.people.urls', namespace='people')),
    path('ss/', include('sundayschool.urls', namespace='sundayschool')),

    # Logout Redirection
    path('logout/', auth_views.LogoutView.as_view(next_page='identity:login'), name='logout'),

    # Dashboard / Entry Point
    path('', dashboard_view, name='dashboard'),

    # Modular Apps (Uncomment these as you create the urls.py inside each app)
    # path('people/', include('apps.people.urls', namespace='people')),
    path('melody/', include('apps.melody.urls', namespace='melody')),
    # path('identity/', include('apps.identity.urls', namespace='identity')),
]