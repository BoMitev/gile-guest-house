from django.contrib import admin
from django.urls import path, include, re_path
from hotel_gile.main_app.views import calc_price, check_room

urlpatterns = [
    re_path(r'admin/calc_price/', calc_price),
    re_path(r'admin/check_rooms/', check_room),
    path('admin/', admin.site.urls),
    path('', include('hotel_gile.main_app.urls'))
]
