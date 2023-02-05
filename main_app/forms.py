from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime

from hotel_gile import settings
from hotel_gile.main_app.models import Contact, Reservation

ADULTS_CHOOSES = (
    (None, ""),
    (1, "1"),
    (2, "2"),
    (3, "3"),
    (4, "4"),
    (5, "5"),
    (6, "6")
)
CHILDREN_CHOOSES = (
    (0, ""),
    (1, "1"),
    (2, "2"),
    (3, "3"),
    (4, "4")
)


class ReservationForm(forms.ModelForm):
    name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'input', 'id': 'name'}))
    phone = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'input', 'id': 'phone', 'inputmode': 'tel'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'id': 'email', 'inputmode': 'email'}))
    check_in = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS, widget=forms.TextInput(attrs={'class': 'check_in', 'id': 'date-in', 'inputmode':'none'}))
    check_out = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS, widget=forms.TextInput(attrs={'class': 'check_out', 'id': 'date-out', 'inputmode':'none'}))
    adults = forms.ChoiceField(choices=ADULTS_CHOOSES, label="", initial='',
                               widget=forms.Select(attrs={'id': 'guest'}))
    children = forms.ChoiceField(choices=CHILDREN_CHOOSES, label="", initial='',
                                 widget=forms.Select(attrs={'id': 'childs'}), required=False)

    class Meta:
        model = Reservation
        fields = ('name', 'phone', 'email','check_in', 'check_out', 'adults', 'children')

    def clean_check_in(self):
        check_in = datetime.combine(self.cleaned_data['check_in'], datetime.strptime("14:00:00", '%H:%M:%S').time())
        return check_in

    def clean_check_out(self):
        check_in = self.cleaned_data['check_in']
        check_out = datetime.combine(self.cleaned_data['check_out'], datetime.strptime("12:00:00", '%H:%M:%S').time())

        if check_out <= check_in:
            raise ValidationError('')

        return datetime.combine(check_out, datetime.strptime("12:00:00", '%H:%M:%S').time())

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
