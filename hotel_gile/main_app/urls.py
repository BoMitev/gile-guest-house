from django.shortcuts import redirect
from django.urls import path, re_path
from django.views.static import serve
from hotel_gile.main_app.views import change_session_language, rooms, contacts, gallery, home, view_404, privacy_policy, basic_terms
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

admin.site.site_header = "ГИЛЕ Администрация"
admin.site.site_title = "ГИЛЕ Администрация"

urlpatterns = [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT, }),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    path('', lambda request: redirect('home'), name="index"),
    path('change_language/', change_session_language, name='change language'),
    path('home/', home, name='home'),
    path('rooms/', rooms, name='rooms'),
    path('contacts/', contacts, name='contacts'),
    path('gallery/', gallery, name='gallery'),
    path('gallery/<int:num>', gallery, name='gallerypage'),
    path('privacy_policy/', privacy_policy, name='privacy_policy'),
    path('basic_terms/', basic_terms, name='basic_terms'),
    re_path(r'^.*/$', view_404)
]

if settings.DEBUG:
    urlpatterns += (
            static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) +
            static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    )
