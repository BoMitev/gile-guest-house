import inspect

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from hotel_gile.main_app.models import Room, HeroGallery, \
    Reviews, Gallery, TermWorkListCol, PaymentLogs
from hotel_gile.main_app.forms import ContactForm, ReservationForm
import hotel_gile.main_app.language_config as lang_config
import hotel_gile.main_app.functions.auxiliary_func as af


@login_required
def payment_logs(request, num=1):
    import math

    logs_per_page = 9
    logs_count = PaymentLogs.objects.count()
    logs_objects = PaymentLogs.objects.all().order_by('-pk')[(logs_per_page * (num - 1)):(logs_per_page * num)]
    pages = math.ceil(logs_count / logs_per_page)

    context = {
        'page_title': "Logs",
        'pages': range(max(1, num-2), (min(pages+1, num+3))),
        'logs': logs_objects,
        'current_page': num
    }

    return render(request, 'payment_logs.html', context)


def view_404(request):
    return redirect('index')


def change_session_language(request):
    request.session['language'] = 'bg' if request.session['language'] == 'en' else 'en'
    request.session.save()
    return redirect(request.META.get('HTTP_REFERER'))


def home(request):
    language = af.get_session_language(request.session)
    page_dynamics = dict(map(lambda x: (x[0], x[1]),
                             TermWorkListCol.objects.filter(link__language=language).
                             values_list('column_ident', 'column_description')))
    rooms = Room.objects.all()[:4]
    hero_gallery = HeroGallery.objects.all()
    reviews = Reviews.objects.all()

    context = {
        'page_title': lang_config.STATICS[language]['menu'][inspect.stack()[0][3]],
        'language': language,
        'hero_gallery': hero_gallery,
        'page_dynamics': page_dynamics,
        'page_statics': lang_config.STATICS[language],
        'rooms': rooms,
        'reservation_form': ReservationForm(),
        'reviews': reviews,
    }

    if request.method == 'POST':
        reservation_form = ReservationForm(request.POST)
        if reservation_form.is_valid():
            context['reservation_submited'] = True
            reservation_form.save()
        else:
            context['reservation_form'] = reservation_form

    return render(request, f'home.html', context)


def rooms(request):
    language = af.get_session_language(request.session)
    page_dynamics = dict(map(lambda x: (x[0], x[1]),
                             TermWorkListCol.objects.filter(link__language=language).
                             values_list('column_ident', 'column_description')))
    rooms = Room.objects.all()

    context = {
        'page_title': lang_config.STATICS[language]['menu'][inspect.stack()[0][3]],
        'language': language,
        'page_dynamics': page_dynamics,
        'rooms': rooms,
        'page_statics': lang_config.STATICS[language],
    }

    return render(request, f'rooms.html', context)


def contacts(request):
    language = af.get_session_language(request.session)
    page_dynamics = dict(map(lambda x: (x[0], x[1]),
                             TermWorkListCol.objects.filter(link__language=language).
                             values_list('column_ident', 'column_description')))

    context = {
        'page_title': lang_config.STATICS[language]['menu'][inspect.stack()[0][3]],
        'language': language,
        'page_dynamics': page_dynamics,
        'rooms': rooms,
        'page_statics': lang_config.STATICS[language],
        'contact_form': ContactForm(),
    }

    if request.method == 'POST':
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            context['message_submited'] = True
            contact_form.save()

    return render(request, f'contact.html', context)


def gallery(request, num=1):
    import math

    images_per_page = 9
    language = af.get_session_language(request.session)
    page_dynamics = dict(map(lambda x: (x[0], x[1]),
                             TermWorkListCol.objects.filter(link__language=language).
                             values_list('column_ident', 'column_description')))
    images = Gallery.objects.all().order_by('-pk')[(images_per_page * (num - 1)):(images_per_page * num)]
    total_images = Gallery.objects.count()
    pages = math.ceil(total_images / images_per_page)

    context = {
        'page_title': lang_config.STATICS[language]['menu'][inspect.stack()[0][3]],
        'language': language,
        'page_dynamics': page_dynamics,
        'page_statics': lang_config.STATICS[language],
        'images': images,
        'pages': range(max(1, num - 2), (min(pages + 1, num + 3))),
        'current_page': num
    }

    return render(request, 'gallery.html', context)


def privacy_policy(request):
    language = af.get_session_language(request.session)
    page_dynamics = dict(map(lambda x: (x[0], x[1]),
                             TermWorkListCol.objects.filter(link__language=language).
                             values_list('column_ident', 'column_description')))

    context = {
        'page_title': lang_config.STATICS[language]["footer"]["privacy_policy"],
        'language': language,
        'page_dynamics': page_dynamics,
        'page_statics': lang_config.STATICS[language],
    }

    return render(request, f'privacy_policy.html', context)


def basic_terms(request):
    language = af.get_session_language(request.session)
    page_dynamics = dict(map(lambda x: (x[0], x[1]),
                             TermWorkListCol.objects.filter(link__language=language).
                             values_list('column_ident', 'column_description')))

    context = {
        'page_title': lang_config.STATICS[language]["footer"]["basic_terms"],
        'language': language,
        'page_dynamics': page_dynamics,
        'page_statics': lang_config.STATICS[language],
    }

    return render(request, f'basic_terms.html', context)


def payment_methods(request):
    language = af.get_session_language(request.session)
    page_dynamics = dict(map(lambda x: (x[0], x[1]),
                             TermWorkListCol.objects.filter(link__language=language).
                             values_list('column_ident', 'column_description')))

    context = {
        'page_title': lang_config.STATICS[language]["footer"]["payment_methods"],
        'language': language,
        'page_dynamics': page_dynamics,
        'page_statics': lang_config.STATICS[language],
    }

    return render(request, f'payment_methods.html', context)
