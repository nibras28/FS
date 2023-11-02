from django.contrib import admin
from django.urls import include, path

from FSCloud import views

urlpatterns = [
    path('', views.home_view, name='home'),  # Set the homepage to the 'home_view'
    path('admin/', admin.site.urls),
    path('app/', include('FSCloud.urls')),  # Include your app's URLs
]
