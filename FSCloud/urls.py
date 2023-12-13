from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('index/', views.index_view, name='index'),
    path('list_data/', views.list_data, name='list_data'),
    path('view_csv/<str:file_name>/', views.view_csv, name='view_csv'),
    path('download_csv/<str:file_name>/', views.download_csv, name='download_csv'),
    path('download_pdf/<str:file_name>/', views.download_pdf, name='download_pdf'),
    path('download_excel/<str:file_name>/', views.download_excel, name='download_excel'),
    path('download_word/<str:file_name>/', views.download_word, name='download_word'),
    path('api/upload/', views.api_upload_file, name='api_upload_file'),
    # ... other URL patterns ...
]
