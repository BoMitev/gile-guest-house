import inspect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse
from hotel_gile.main_app.models import TermWorkList, Page, PageSection, Room, HeroGallery, \
    Reviews, Gallery, Reservation
from hotel_gile.main_app.forms import ContactForm, ReservationForm
import hotel_gile.main_app.language_config as lang_config
import hotel_gile.main_app.auxiliary_functions as af


@login_required
def calc_price(request):
    from datetime import datetime

    room = int(request.GET.get('room'))
    adults = int(request.GET.get('adults'))
    children = int(request.GET.get('children'))
    check_in = datetime.strptime(request.GET.get('check_in'), '%d.%m.%Y')
    check_out = datetime.strptime(request.GET.get('check_out'), '%d.%m.%Y')
    room_obj = Room.objects.get(id=room)
    total_guests = adults + children

    discount = 0
    if request.GET.get('discount'):
        discount = float(request.GET.get('discount'))

    reservation = Reservation(name="Test", phone="0881234123", email="test@test.com", room=room_obj,
                              adults=adults, children=children, check_in=check_in, check_out=check_out, discount=discount)

    if room < 1 or total_guests < 1 or reservation.calc_days < 1:
        return HttpResponse(f"0.00 лв.")

    if total_guests > room_obj.room_capacity:
        return HttpResponse("Недостатъчен капацитет")

    price = af.calculate_reservation_price(reservation)
    return HttpResponse(f"{price:.2f} лв.")


def view_404(request):
    return redirect('index')


def change_session_language(request):
    if request.session['language'] == 'bg':
        request.session['language'] = 'en'
    else:
        request.session['language'] = 'bg'
    request.session.save()
    return redirect(request.META.get('HTTP_REFERER'))


def home(request):
    language = af.get_session_language(request.session)
    page_dynamics = TermWorkList.objects.get(language=language)
    page_data = Page.objects.get(page_name="Home", language=language)
    page_sections = PageSection.objects.filter(page__exact=page_data).all()
    rooms = Room.objects.all()[:4]
    hero_gallery = HeroGallery.objects.all()
    reviews = Reviews.objects.all()

    context = {
        'page_title': lang_config.STATICS[language]['menu'][inspect.stack()[0][3]],
        'language': language,
        'hero_gallery': hero_gallery,
        'page_sections': page_sections,
        'page_dynamics': page_dynamics,
        'page_data': page_data,
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
    page_dynamics = TermWorkList.objects.get(language=language)
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
    page_dynamics = TermWorkList.objects.get(language=language)

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


def gallery(request):
    language = af.get_session_language(request.session)
    page_dynamics = TermWorkList.objects.get(language=language)
    images = Gallery.objects.all().order_by('-pk')

    context = {
        'page_title': lang_config.STATICS[language]['menu'][inspect.stack()[0][3]],
        'language': language,
        'page_dynamics': page_dynamics,
        'page_statics': lang_config.STATICS[language],
        'images': images,
    }

    return render(request, 'gallery.html', context)
