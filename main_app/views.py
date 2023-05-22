import inspect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse
from hotel_gile.main_app.models import TermWorkList, Page, PageSection, Room, HeroGallery, \
    Reviews, Gallery, Reservation, ReservedRooms
from hotel_gile.main_app.forms import ContactForm, ReservationForm
import hotel_gile.main_app.language_config as lang_config
import hotel_gile.main_app.auxiliary_functions as af
from datetime import datetime
import json


@login_required
def calc_price(request):
    if not request.GET:
        return HttpResponse("OK")

    room = int(request.GET.get('room'))
    adults = int(request.GET.get('adults'))
    children = int(request.GET.get('children'))
    discount = request.GET.get('discount')
    discount = float(discount) if discount else 0
    check_in = datetime.strptime(request.GET.get('check_in'), '%d.%m.%Y')
    check_out = datetime.strptime(request.GET.get('check_out'), '%d.%m.%Y')
    total_guests = children + adults

    room_obj = Room.objects.get(id=room)
    if total_guests > room_obj.room_capacity:
        return HttpResponse(json.dumps({'price_per_night': 'Няма капацитет', 'total': 'Няма капацитет'}))

    res_id_str = request.META.get('HTTP_REFERER').split("/")[6]
    res_id = int(res_id_str) if res_id_str.isnumeric() else 0

    if res_id:
        temp_reservation = Reservation.objects.get(pk=res_id)
    else:
        temp_reservation = Reservation(check_in=check_in, check_out=check_out)
    temp_room = ReservedRooms(reservation=temp_reservation, room=room_obj, adults=adults, children=children, discount=discount)

    dump = json.dumps({'price_per_night': f"{temp_room.price_per_night:.2f} лв.", 'total': f"{temp_room.total_price:.2f} лв."})
    return HttpResponse(dump)


@login_required
def check_room(request):
    check_in = datetime.strptime(request.GET.get('check_in'), '%d.%m.%Y')
    check_out = datetime.strptime(request.GET.get('check_out'), '%d.%m.%Y')
    reservation = int(request.GET.get('reservation'))

    result = {}

    from hotel_gile.main_app.technical_functions.technical_functions import get_all_free_rooms
    from hotel_gile.main_app.models import ReservedRooms
    all_rooms = get_all_free_rooms(check_in, check_out, reservation, reservedrooms=ReservedRooms, room=Room)
    for room in all_rooms:
        result[str(room.id)] = room.title

    dump = json.dumps(result)

    return HttpResponse(dump)


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


def gallery(request, num=1):
    import math

    images_per_page = 9
    language = af.get_session_language(request.session)
    page_dynamics = TermWorkList.objects.get(language=language)
    images = Gallery.objects.all().order_by('-pk')[(images_per_page*(num-1)):(images_per_page*num)]
    total_images = Gallery.objects.count()
    pages = math.ceil(total_images / images_per_page)

    context = {
        'page_title': lang_config.STATICS[language]['menu'][inspect.stack()[0][3]],
        'language': language,
        'page_dynamics': page_dynamics,
        'page_statics': lang_config.STATICS[language],
        'images': images,
        'pages': range(max(1, num-2), (min(pages+1, num+3))),
        'current_page': num
    }

    return render(request, 'gallery.html', context)
