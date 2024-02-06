from django.db import models


class LanguageEnum(models.TextChoices):
    EN = 'en', 'English'
    BG = 'bg', 'Български'


class ReservationStatus(models.TextChoices):
    PENDING = '0', 'Заявена'
    ACCEPTED = '1', 'Потвърдена'
    PAID_BY_BOOKING = '2', 'Платена през Booking'
    PAID = '3', 'Платена'