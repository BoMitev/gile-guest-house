from django.urls import path
from .views import CalcRoomPrice, CheckRoom, Payments

urlpatterns = [
    path(r'calc_price/', CalcRoomPrice.as_view(), name='calc_price'),
    path(r'check_rooms/', CheckRoom.as_view(), name='check_room'),
    path(r'payments/', Payments.as_view(), name='payments')
]