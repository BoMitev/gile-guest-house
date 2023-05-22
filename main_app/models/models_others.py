from django.db import models
from django.utils.safestring import mark_safe


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

    @property
    def stars(self):
        return self.score / 2

    class Meta:
        verbose_name = 'Отзив'
        verbose_name_plural = '8. Отзиви'

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

    def __str__(self):
        return f"Снимка {self.id}"


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
        verbose_name = 'Запитване'
        verbose_name_plural = '2. Запитвания'
