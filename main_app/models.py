from datetime import datetime
import locale
from django.contrib import admin
from django.db import models
from django.db.models import Q
from django.utils.safestring import mark_safe
import hotel_gile.main_app.validators as validators
import hotel_gile.main_app.auxiliary_functions as af
from hotel_gile.settings import ADMIN_LIST_DISPLAY_DATETIME_FORMAT, ADMIN_LIST_DISPLAY_DATE_FORMAT

BOOL_CHOICES = ((True, 'Да'), (False, 'Не'))

LANGUAGES_CHOISES = [
    ('en', "English"),
    ('bg', 'Български')
]


class HeroGallery(models.Model):
    image = models.ImageField(upload_to="hero/", verbose_name="Качи снимка")

    class Meta:
        verbose_name = "Начална Галерия"
        verbose_name_plural = "5. Начална Галерия"

    @property
    def thumbnail_preview(self):
        if self.image:
            return mark_safe(f'<img src="{self.image.url}" width="250" height="250" style="object-fit: cover;" alt="Няма снимка" />')
        return ""
    thumbnail_preview.fget.short_description = 'Преглед'

    def __str__(self):
        return "Снимка"


class Room(models.Model):
    id = models.IntegerField(primary_key=True, verbose_name="Номер на стая")
    room_title = models.CharField(max_length=100, verbose_name="Име на стая")
    room_title_en = models.CharField(max_length=100, verbose_name="Name of room")
    room_capacity = models.IntegerField(verbose_name="Капацитет", help_text="Максимален брой гости")
    room_size = models.IntegerField(verbose_name="Квадратура")
    room_services = models.TextField(verbose_name="Екстри")
    room_services_en = models.TextField(verbose_name="Services")
    min_price = models.IntegerField(verbose_name='Минимална цена', help_text="При минимален брой гости")
    price = models.IntegerField(verbose_name="Цена", help_text="При максимален брой гости")
    discount_per_person = models.FloatField(verbose_name='Отсъпка на човек', help_text="Отстъпка при непълен капацитет")
    image = models.ImageField(upload_to="room/", verbose_name="Качи снимка")

    class Meta:
        verbose_name = "Стая"
        verbose_name_plural = "4. Стаи"

    @property
    def title(self):
        return f"№{self.id}: {self.room_title}"

    @property
    def title_en(self):
        return f"№{self.id}: {self.room_title_en}"

    @property
    def thumbnail_preview(self):
        if self.image:
            return mark_safe('<img src="{}" width="250" alt="Няма снимка" />'.format(self.image.url))
        return ""
    thumbnail_preview.fget.short_description = 'Преглед'

    def __str__(self):
        return f"№{self.id}: {self.room_title} - {self.price}лв."


class Reservation(models.Model):
    external_id = models.CharField(max_length=32, unique=True, blank=True, null=True)
    confirm = models.BooleanField(default=False, blank=True, verbose_name="Потвърждаване")
    name = models.CharField(max_length=150, verbose_name="Имена")
    phone = models.CharField(max_length=25, verbose_name="Телефон за връзка")
    email = models.EmailField(blank=True, null=True, verbose_name="Имейл")
    check_in = models.DateTimeField(verbose_name="Настаняване", default=af.default_check_in)
    check_out = models.DateField(verbose_name="Напускане", default=af.default_check_out)
    adults = models.PositiveIntegerField(verbose_name="Брой възрастни")
    children = models.PositiveIntegerField(verbose_name="Брой деца", blank=True, null=True, default=0)
    description = models.TextField(verbose_name='Коментар', blank=True, null=True)
    room = models.ForeignKey(Room, verbose_name="Стая", blank=True, null=True, on_delete=models.SET_NULL)
    price = models.FloatField(verbose_name='Цена', blank=True, null=True, default=0)
    discount = models.FloatField(verbose_name='Отстъпка/ Надценка', blank=True, null=True)
    added_on = models.DateTimeField(verbose_name='Резервирана на', blank=True, default=datetime.now)
    archived = models.BooleanField(default=False, blank=True, choices=BOOL_CHOICES, verbose_name="Архивиране",
                                   help_text="Резервациите се архивират автоматично, след като изтече датата на напускане!")

    @property
    def total_guests(self):
        return self.adults + self.children

    @admin.display(boolean=True, description="С")
    def status_admin(self):
        return self.confirm

    @admin.display(description="Настаняване")
    def check_in_admin(self):
        locale.setlocale(locale.LC_TIME, "bg_BG")
        check_in = self.check_in
        return check_in.strftime(ADMIN_LIST_DISPLAY_DATETIME_FORMAT)

    @admin.display(description="Резервирана")
    def added_on_admin(self):
        locale.setlocale(locale.LC_TIME, "bg_BG")
        added_on = self.added_on
        return added_on.strftime(ADMIN_LIST_DISPLAY_DATETIME_FORMAT)

    @admin.display(description="Напускане")
    def check_out_admin(self):
        locale.setlocale(locale.LC_TIME, "bg_BG")
        check_out = self.check_out
        return check_out.strftime(ADMIN_LIST_DISPLAY_DATE_FORMAT)

    @property
    def calc_days(self):
        return abs(self.check_in.date() - self.check_out).days
    calc_days.fget.short_description = 'Нощувки'

    @property
    def title(self):
        if isinstance(self.room, Room):
            return f'Стая №{self.room.id}'
        return f'НЕ Е ИЗБРАНА СТАЯ'
    title.fget.short_description="Стая"

    @property
    def price_currency(self):
        return f"{self.price} лв."
    price_currency.fget.short_description = "Цена"

    def is_room_busy(self):
        return Reservation.objects.exclude(id=self.id).filter(
            (Q(check_in__range=(self.check_in, self.check_out)) & Q(room=self.room))
            | (Q(check_out__range=(self.check_in, self.check_out)) & Q(room=self.room))
            | (Q(check_in__lte=self.check_in, check_out__gt=self.check_out)) & Q(room=self.room)).last()

    def clean(self):
        validators.validate_dates(self)
        self.name = self.name.title()

        if self.children is None:
            self.children = 0

        if not self.pk and not self.room:
            af.send_notification_email(self)

        if self.room:
            is_room_busy = self.is_room_busy()
            validators.is_room_busy(is_room_busy)
            validators.is_room_capacity_exceeded(self)
        else:
            validators.is_room_choosen(self)

    class Meta:
        verbose_name = "Резервация"
        verbose_name_plural = "1. Резервации"

    def __str__(self):
        return self.title


class ArchivedReservation(Reservation):
    class Meta:
        proxy = True
        verbose_name = "Архивирана резервация"
        verbose_name_plural = "9. Архивирани резервации"

    def __str__(self):
        return self.title


class Reviews(models.Model):
    review_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30, verbose_name="Име")
    pros = models.TextField(verbose_name='Предимства')
    cons = models.TextField(verbose_name='Недостатъци')
    score = models.CharField(max_length=5, verbose_name='Оценка')

    class Meta:
        verbose_name = 'Ревю'
        verbose_name_plural = '8. Ревюта'

    def __str__(self):
        return self.name


class Page(models.Model):
    page_name = models.CharField(max_length=50)
    language = models.CharField(max_length=2, choices=LANGUAGES_CHOISES)

    class Meta:
        verbose_name = "Начална страница"
        verbose_name_plural = "6. Начална страница"

    def __str__(self):
        return self.page_name


class PageSection(models.Model):
    section_title = models.CharField(max_length=150, blank=True)
    section_description = models.TextField(blank=True)
    page = models.ForeignKey(Page, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Секция"
        verbose_name_plural = "Секции"

    def __str__(self):
        return self.section_title


class Gallery(models.Model):
    image = models.ImageField(upload_to="gallery/", verbose_name="Качи снимка")

    @property
    def thumbnail_preview(self):
        if self.image:
            return mark_safe(f'<img src="{self.image.url}" width="250" height="250" style="object-fit: contain;" alt="Няма снимка" />')
        return ""
    thumbnail_preview.fget.short_description = 'Преглед'

    class Meta:
        verbose_name = "Галерия"
        verbose_name_plural = "3. Галерия"


class TermWorkList(models.Model):
    language = models.CharField(max_length=2, choices=LANGUAGES_CHOISES)
    phone = models.CharField(max_length=25, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    booking_url = models.URLField(blank=True, null=True)
    facebook_url = models.URLField(blank=True, null=True)
    footer_slogan = models.CharField(max_length=80, blank=True, null=True)
    footer_contacts = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Термини"

    class Meta:
        verbose_name = "Термини"
        verbose_name_plural = "7. Термини"


class Contact(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return f"Запитване от {self.name} ( {self.email} )"

    class Meta:
        verbose_name = 'Съобщения'
        verbose_name_plural = '2. Съобщения'
