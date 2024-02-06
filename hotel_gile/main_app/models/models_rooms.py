from django.db import models
from django.utils.safestring import mark_safe
from simple_history.models import HistoricalRecords


class Room(models.Model):
    id = models.IntegerField(primary_key=True, verbose_name="№ стая")
    room_title = models.CharField(max_length=100, verbose_name="Име на стая")
    room_title_en = models.CharField(max_length=100, verbose_name="Name of room", help_text="На английски")
    room_capacity = models.IntegerField(verbose_name="Капацитет", help_text="Максимален брой гости")
    room_size = models.IntegerField(verbose_name="Квадратура", help_text="м3")
    room_services = models.TextField(verbose_name="Екстри")
    room_services_en = models.TextField(verbose_name="Services", help_text="На английски")
    image = models.ImageField(upload_to="room/", verbose_name="Качи снимка")

    class Meta:
        verbose_name = "Стая"
        verbose_name_plural = "4. Стаи"

    @property
    def title(self):
        return f"№{self.id}: {self.room_title}"
    title.fget.short_description = "Стая"

    @property
    def title_en(self):
        return f"№{self.id}: {self.room_title_en}"

    @property
    def max_price(self):
        return RoomPrice.objects.get(room=self, persons=self.room_capacity).price
    max_price.fget.short_description = "Цена"

    @property
    def min_price(self):
        return RoomPrice.objects.get(room=self, persons=1).price

    @property
    def thumbnail_preview(self):
        if self.image:
            return mark_safe('<img src="{}" width="250" alt="Няма снимка" />'.format(self.image.url))
        return ""
    thumbnail_preview.fget.short_description = 'Преглед'

    def price_per_night(self, persons, at_date):
        try:
            price = RoomPrice.history.filter(history_date__lte=at_date, room_id=self.id, persons=persons).first().price
        except Exception as ex:
            price = RoomPrice.objects.get(room=self, persons=persons).price
        return price

    def __str__(self):
        return f"№{self.id}: {self.room_title}."


class RoomPrice(models.Model):
    persons = models.IntegerField(blank=True)
    price = models.FloatField(verbose_name='Цена', null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Цена"
        verbose_name_plural = "Ценоразпис"
        unique_together = ('id', 'room', 'persons')

    def save(self, *args, **kwargs):
        if not self.pk:
            self.persons = RoomPrice.objects.filter(room=self.room).count() + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.persons} човек/а"
