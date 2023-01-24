from django.shortcuts import redirect
from django.urls import path, re_path
from django.views.static import serve
from hotel_gile.main_app.views import change_session_language, rooms, contacts, gallery, home
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

admin.site.site_header = "ГИЛЕ Администрация"
admin.site.site_title = "ГИЛЕ Администрация"

urlpatterns = [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT, }),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    path('', lambda request: redirect('home')),
    path('change_language/', change_session_language, name='change language'),
    path('home/', home, name='home'),
    path('rooms/', rooms, name='rooms'),
    path('contacts/', contacts, name='contacts'),
    path('gallery/', gallery, name='gallery')
]

if settings.DEBUG:
    urlpatterns += (
        static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) +
        static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
        )