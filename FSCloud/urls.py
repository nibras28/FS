from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('index/', views.index_view, name='index'),
    path('list_data/', views.list_data, name='list_data'),
    path('view_csv/<str:file_name>/', views.view_csv, name='view_csv'),
    # ... other URL patterns ...
]
