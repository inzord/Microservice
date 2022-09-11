from django.urls import path
from . import views

urlpatterns = {
    path('', views.get_data),
    path('get_by_key', views.get_by_key)
}
