from django.contrib import admin
from django.utils.html import format_html
import hotel_gile.main_app.functions.auxiliary_functions as af
from admin_extra_buttons.api import ExtraButtonsMixin, button
from hotel_gile.main_app.models import TermWorkList, TermWorkListCol, HeroGallery, Contact, Reviews, Gallery


class TermWorkListColInlineAdmin(admin.TabularInline):
    model = TermWorkListCol
    extra = 1
    verbose_name = "атрибут"
    verbose_name_plural = "атрибути"

    def get_fieldsets(self, request, obj=None):
        return (
            ('', {
                'fields': ('column_ident', 'column_description')
            }),
        )


@admin.register(TermWorkList)
class TermWorkListAdmin(admin.ModelAdmin):
    list_display = ('language',)
    inlines = (TermWorkListColInlineAdmin,)

    # def has_add_permission(self, request):
    #     return False
    #
    # def has_delete_permission(self, request, obj=None):
    #     return False


@admin.register(HeroGallery)
class HeroGallleryAdmin(admin.ModelAdmin):
    list_display = ('thumbnail_preview',)
    readonly_fields = ('thumbnail_preview',)


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('thumbnail_preview',)
    readonly_fields = ('thumbnail_preview',)
    list_per_page = 9


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description='email')
    def email_link(self, obj):
        return format_html("<a href='mailto:{email}'>{email}</a>", email=obj.email)

    email_link.allow_tags = True

    fieldsets = (
        ('', {
            'fields': ('name', 'email_link', 'message')
        }),
    )


@admin.register(Reviews)
class ReviewsAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    list_display = ('name', 'score', 'date')
    ordering = ('-date',)
    list_per_page = 15
    search_fields = ['name__icontains', ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @button(html_attrs={'style': 'background-color:#88FF88;color:black'}, label='Зареди отзиви')
    def load(self, request):
        self.message_user(request, 'Зареждане на отзиви от Booking.com')
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

            Reviews.objects.bulk_create(objects, update_conflicts=True, unique_fields=['review_id'],
                                        update_fields=['name', 'pros', 'cons', 'score', 'date', 'check_in', 'check_out',
                                                       'room'])

        return

    fieldsets = (
        ('Отзив:', {
            'fields': ('name', 'pros', 'cons', 'score', 'date')
        }),
        ('От резервация:', {
            'fields': ('room', ('check_in', 'check_out'))
        }),
    )
