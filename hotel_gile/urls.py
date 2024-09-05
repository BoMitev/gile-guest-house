from django.contrib import admin
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('admin/', admin.site.urls),
    path('rest/', include('hotel_gile.rest.urls')),
    path('', include('hotel_gile.main_app.urls')),

]
