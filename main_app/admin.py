from datetime import date, datetime, timedelta
from admin_extra_buttons.api import ExtraButtonsMixin, button, confirm_action, link, view
from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from hotel_gile.main_app.models import Room, Page, PageSection, TermWorkList, HeroGallery, Contact, \
    Reviews, Gallery, Reservation, ArchivedReservation, RoomPrice
import hotel_gile.main_app.auxiliary_functions as af

admin.site.unregister(Group)


class PageSectionInlineAdmin(admin.StackedInline):
    model = PageSection
    extra = 1

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class RoomPriceInlineAdmin(admin.TabularInline):
    exclude = ('persons',)
    model = RoomPrice
    extra = 0

    def get_min_num(self, request, obj=None, **kwargs):
        return obj.room_capacity if obj else 0

    def get_max_num(self, request, obj=None, **kwargs):
        return obj.room_capacity if obj else 0

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('title', 'room_title_en', 'max_price')
    readonly_fields = ('thumbnail_preview', )
    inlines = (RoomPriceInlineAdmin,)
    ordering = ('id',)

    def get_readonly_fields(self, request, obj=None):
        fields = self.readonly_fields
        if obj:
            fields += ('id',)
        return fields

    fieldsets = (
        ('', {
            'fields': (
                'id', ('room_title', 'room_title_en',), ('room_capacity', 'room_size'), 'room_services',
                'room_services_en', ('image', 'thumbnail_preview'))
        }),

    )


@admin.register(Reservation)
class ReservationAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    list_display_links = ("title",)
    list_display = ('status_admin', 'title', 'name', 'calc_days', 'check_in_admin', 'check_out_admin', 'added_on_admin',
                    'price_currency')
    search_fields = ['name__icontains', 'id__iexact']
    readonly_fields = ('price_currency', 'id')
    list_per_page = 15
    ordering = ('confirm', 'check_in', 'check_out', 'room_id')

    def get_queryset(self, request):
        # qs = Reservation.objects.all()
        # for reserv in qs:
        #     reserv.check_out = reserv.check_out.strftime('%Y-%m-%d 12:00:00')
        #     reserv.save()

        return Reservation.objects.filter(check_out__gte=datetime.today())

    def get_form(self, request, obj=None, **kwargs):
        form = super(ReservationAdmin, self).get_form(request, obj, **kwargs)
        field = form.base_fields["room"]
        field.widget.can_add_related = False
        field.widget.can_change_related = False
        field.widget.can_delete_related = False
        return form

    def delete_model(self, request, obj):
        if obj.external_id:
            try:
                af.delete_reservation(obj)
            except Exception as ex:
                print(ex)

        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            if obj.external_id:
                try:
                    af.delete_reservation(obj)
                except Exception as ex:
                    print(ex)

        super().delete_model(request, queryset)

    def save_model(self, request, obj, form, change):
        if form.changed_data and not obj.archived:
            if obj.room:
                price = af.calculate_reservation_price(obj)
                obj.price = price
            else:
                obj.price = 0

            if obj.confirm:
                if not obj.email_sent and obj.email:
                    obj.email_sent = af.send_confirmation_email(obj)

                if obj.external_id:
                    af.update_reservation(obj)
                else:
                    external_id = af.send_reservation(obj)
                    obj.external_id = external_id
            else:
                if obj.external_id:
                    af.delete_reservation(obj)
                    obj.external_id = None

        super().save_model(request, obj, form, change)

    def get_fieldsets(self, request, obj=None):
        if obj:
            return (
                ('', {
                    'fields': ('confirm',)
                }),
                ('???????????????????? ????:', {
                    'fields': (('room', 'id'), ('name', 'phone', 'email'),
                               ('check_in', 'check_out'), ('adults', 'children'),
                               'description', ('price_currency', 'discount',))
                }),
            )

        return (
            ('', {
                'fields': ('confirm',)
            }),
            ('???????????????????? ????:', {
                'fields': ('room', ('name', 'phone', 'email'),
                           ('check_in', 'check_out'), ('adults', 'children'),
                           'description', ('price_currency', 'discount',))
            }),
        )


@admin.register(ArchivedReservation)
class ArchivedReservationAdmin(admin.ModelAdmin):
    list_display_links = ("title",)
    list_display = ('title', 'name', 'calc_days', 'check_in_admin', 'check_out_admin', 'added_on_admin',
                    'price_currency')
    search_fields = ['name__icontains', 'id__iexact', 'check_in__icontains', 'check_out__icontains']
    list_per_page = 15
    ordering = ('-check_in', '-check_out', 'room_id')
    exclude = ('id',)

    def has_delete_permission(self, request, obj=None):
        if request.user.id == 1:
            return True
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        return Reservation.objects.filter(check_out__lt=datetime.today())

    fieldsets = (
        ('???????????????????? ????:', {
            'fields': (
                ('room', 'id'), ('name', 'phone', 'email'), ('check_in_admin', 'check_out_admin'),
                ('adults', 'children'), 'description',
                ('price_currency', 'discount',))
        }),
    )


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('language',)
    inlines = (PageSectionInlineAdmin,)
    ordering = ('language',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_fields(self, request, obj=None):
        fields = list(super(PageAdmin, self).get_fields(request, obj))
        exclude_set = set()
        if obj:  # obj will be None on the add page, and something on change pages
            exclude_set.add('page_name')
            exclude_set.add('language')
        return [f for f in fields if f not in exclude_set]


@admin.register(TermWorkList)
class TermWorkListAdmin(admin.ModelAdmin):
    list_display = ('language',)
    readonly_fields = ('language',)
    ordering = ('language',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(HeroGallery)
class HeroGallleryAdmin(admin.ModelAdmin):
    list_display = ('thumbnail_preview',)
    readonly_fields = ('thumbnail_preview',)


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('thumbnail_preview',)
    readonly_fields = ('thumbnail_preview',)


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
    search_fields = ['name__icontains', ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @button(html_attrs={'style': 'background-color:#88FF88;color:black'})
    def load(self, request):
        self.message_user(request, '?????????????????? ???? ?????????????????? ???? Booking.com')
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
        ('??????????:', {
            'fields': ('name', 'pros', 'cons', 'score', 'date')
        }),
        ('???? ????????????????????:', {
            'fields': ('room', ('check_in', 'check_out'))
        }),
    )
