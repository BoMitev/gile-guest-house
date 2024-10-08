from django.db import models, transaction
from django.utils.safestring import mark_safe
from hotel_gile.main_app.models.enums import LanguageEnum
from hotel_gile.main_app.functions import auxiliary_func as af


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

    def __str__(self):
        return f"Снимка {self.id}"


class Reviews(models.Model):
    review_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30, verbose_name="Име")
    pros = models.TextField(verbose_name='Предимства')
    cons = models.TextField(verbose_name='Недостатъци', blank=True, null=True)
    score = models.FloatField(max_length=5, verbose_name='Оценка')
    date = models.DateTimeField(verbose_name="Дата на отзива")
    check_in = models.DateField(verbose_name="Настанен")
    check_out = models.DateField(verbose_name="Напуснал")
    room = models.CharField(max_length=30, verbose_name="Стая")

    @classmethod
    def bulk_create_with_limit(cls):
        reviews, response = af.load_reviews()
        if response == 200:
            objects = [Reviews(review_id=review['review_id'],
                               name=review['author']['name'],
                               pros=review['pros'],
                               cons=review['cons'],
                               score=round(float(review['average_score']) * 2.5, 1),
                               date=review['date'],
                               check_in=review['stayed_room_info']['checkin'],
                               check_out=review['stayed_room_info']['checkout'],
                               room=review['stayed_room_info']['room_name']
                               ) for review in reviews if review['pros']]
            with transaction.atomic():
                # Bulk create or update the records
                cls.objects.bulk_create(
                    objects,
                    update_conflicts=True,
                    unique_fields=['review_id'],
                    update_fields=['name', 'pros', 'cons', 'score', 'date', 'check_in', 'check_out', 'room']
                )

                # Ensure only 20 most recent records remain
                total_records = cls.objects.count()
                if total_records > 20:
                    delete_count = total_records - 20
                    ids_to_delete = cls.objects.order_by('date').values_list('review_id', flat=True)[:delete_count]
                    cls.objects.filter(review_id__in=ids_to_delete).delete()

    @property
    def stars(self):
        return self.score / 2

    class Meta:
        verbose_name = 'Отзив'
        verbose_name_plural = '7. Отзиви'

    def __str__(self):
        return self.name


class TermWorkList(models.Model):
    language = models.CharField(max_length=2, choices=LanguageEnum.choices, null=False, blank=False, unique=True)

    def __str__(self):
        return f"Термини"

    class Meta:
        verbose_name = "Термини"
        verbose_name_plural = "6. Термини"


class TermWorkListCol(models.Model):
    column_ident = models.CharField(max_length=50, db_index=True, verbose_name="Идентификат")
    column_description = models.TextField(blank=True, verbose_name='Съдържание')
    link = models.ForeignKey(TermWorkList, on_delete=models.CASCADE)

    def __str__(self):
        return self.column_ident


class Contact(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return f"Запитване от {self.name} ( {self.email} )"

    class Meta:
        verbose_name = 'Запитване'
        verbose_name_plural = '2. Запитвания'
