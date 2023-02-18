from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime
import hotel_gile.main_app.auxiliary_functions as af
from hotel_gile import settings
from hotel_gile.main_app.models import Contact, Reservation, Room

ROOMS = Room.objects.all().order_by('-room_capacity')
capacity = 0
id = 1
ROOM_CHOICES = []
for room in ROOMS:
    capacity += room.room_capacity
    ROOM_CHOICES.append((capacity, id))
    id += 1

ADULTS_CHOISES = [(i, i) for i in range(1, 24)]
CHILD_CHOISES = [(i, i) for i in range(0, 23)]


class ReservationForm(forms.ModelForm):
    name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'input', 'id': 'name'}))
    phone = forms.CharField(max_length=30,
                            widget=forms.TextInput(attrs={'class': 'input', 'id': 'phone', 'inputmode': 'tel'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'id': 'email', 'inputmode': 'email'}))
    check_in = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS,
                               widget=forms.TextInput(
                                   attrs={'class': 'check_in', 'id': 'date-in', 'inputmode': 'none'}))
    check_out = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS,
                                widget=forms.TextInput(
                                    attrs={'class': 'check_out', 'id': 'date-out', 'inputmode': 'none'}))
    children =  forms.ChoiceField(choices=CHILD_CHOISES, label="",
                              widget=forms.Select(attrs={'id': 'childs', 'onchange': 'calculateMaxCapacity(this)'}), required=False)
    adults = forms.ChoiceField(choices=ADULTS_CHOISES, label="",
                              widget=forms.Select(attrs={'id': 'adults', 'onchange': 'calculateMaxCapacity(this)'}))
    rooms = forms.ChoiceField(choices=ROOM_CHOICES, label="",
                              widget=forms.Select(attrs={'id': 'rooms', 'onchange': 'calculateMaxCapacity(this)'}))

    class Meta:
        model = Reservation
        fields = ('name', 'phone', 'email', 'check_in', 'check_out', 'adults', 'children')

    def save(self, commit=True):
        total_guests = int(self.cleaned_data['adults']) + int(self.cleaned_data['children'])
        rooms = self.cleaned_data['rooms']

        reservations = []
        while total_guests > 0:
            room_guest = int(total_guests / rooms)
            total_guests -= room_guest
            rooms -= 1

            reservations.append(
                Reservation(
                    name=self.cleaned_data['name'],
                    phone=self.cleaned_data['phone'],
                    email=self.cleaned_data['email'],
                    check_in=self.cleaned_data['check_in'],
                    check_out=self.cleaned_data['check_out'],
                    adults=room_guest
                )
            )
        Reservation.objects.bulk_create(reservations, ignore_conflicts=True)

    def clean(self):
        if (self.cleaned_data['adults'] + self.cleaned_data['children']) < self.cleaned_data['rooms']:
            raise ValidationError({"adults": ""})

        af.send_notification_email(self)

    def clean_name(self):
        return self.cleaned_data['name'].title()

    def clean_check_in(self):
        check_in = datetime.combine(self.cleaned_data['check_in'], datetime.strptime("14:00:00", '%H:%M:%S').time())
        return check_in

    def clean_check_out(self):
        check_in = self.cleaned_data['check_in']
        check_out = datetime.combine(self.cleaned_data['check_out'], datetime.strptime("12:00:00", '%H:%M:%S').time())

        if check_out <= check_in:
            raise ValidationError('')

        return datetime.combine(check_out, datetime.strptime("12:00:00", '%H:%M:%S').time())

    def clean_rooms(self):
        return [v for (k, v) in self.base_fields['rooms'].choices if k == int(self.cleaned_data['rooms'])][0]

    def clean_children(self):
        children = self.cleaned_data.get('children', 0)
        return int(children)

    def clean_adults(self):
        return int(self.cleaned_data['adults'])

    def clean_phone(self):
        import phonenumbers

        phone_number = self.cleaned_data['phone']
        try:
            if phone_number.startswith('00'):
                my_number = phonenumbers.parse("+" + phone_number[2:])
            elif phone_number.startswith('0'):
                my_number = phonenumbers.parse("+359" + phone_number[1:])
            else:
                my_number = phonenumbers.parse(phone_number)
            status = phonenumbers.is_possible_number(my_number)
        except Exception as ex:
            status = False

        if not status:
            raise ValidationError('')

        return phone_number


class ContactForm(forms.ModelForm):
    name = forms.CharField(max_length=50, )
    email = forms.EmailField()
    message = forms.Textarea()

    class Meta:
        model = Contact
        fields = "__all__"
