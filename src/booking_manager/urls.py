from django.urls import path, include
from booking_manager.views import index, index_2

urlpatterns = [
    path('index/', index),
    path('base/<int:booking_id>', index_2),
]