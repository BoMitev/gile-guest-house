from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('rest/', include('hotel_gile.rest.urls')),
    path('', include('hotel_gile.main_app.urls'))

]
