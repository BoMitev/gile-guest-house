from datetime import date
from admin_extra_buttons.api import ExtraButtonsMixin, button, confirm_action, link, view
from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from hotel_gile.main_app.models import Room, Page, PageSection, TermWorkList, HeroGallery, Contact, \
    Reviews, Gallery, Reservation, ArchivedReservation
import hotel_gile.main_app.auxiliary_functions as af



admin.site.unregister(Group)


class PageSectionInlineAdmin(admin.StackedInline):
    model = PageSection
    extra = 1

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('title', 'price',)
    readonly_fields = ('thumbnail_preview',)
    ordering = ('id',)

    def save_model(self, request, obj, form, change):
        if 'id' in form.changed_data and not request.path.find("add"):
            old_id = form.initial['id']
            room = Room.objects.get(id=old_id)
            room.delete()
        super().save_model(request, obj, form, change)

    fieldsets = (
        ('', {
            'fields': (
                ('room_title', 'room_title_en',), 'room_capacity', 'room_size', 'room_services', 'room_services_en', ('price', 'min_price', 'discount_per_person'), ('image', 'thumbnail_preview'))
        }),
    )


@admin.register(Reservation)
class ReservationAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    list_display_links = ("title",)
    list_display = ("status_admin", 'title', 'name', 'calc_days', 'check_in_admin', 'check_out_admin', 'added_on_admin', 'price_currency')
    exclude = ('id',)
    readonly_fields = ('price_currency',)
    list_per_page = 15
    ordering = ('check_in', 'check_out', 'room_id')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        for reservation in qs:
            if reservation.check_out < date.today():
                reservation.archived = True
                reservation.save()
        return qs.filter(archived=False)

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
            except:
                pass

        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            if obj.external_id:
                try:
                    af.delete_reservation(obj)
                except:
                    pass

        super().delete_model(request, queryset)

    def save_model(self, request, obj, form, change):
        if form.changed_data:
            if not obj.archived:
                if obj.room:
                    price = af.calculate_reservation_price(obj)
                    obj.price = price
                else:
                    obj.price = 0

                if obj.confirm:
                    if "confirm" in form.changed_data and obj.email:
                        af.send_confirmation_email(obj)

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

    # @button(html_attrs={'style': 'background-color:#DBC913;color:black'})
    # def load(self, request):
    #     reservations = af.load_reservations()
    #     for reservation in reservations:
    #         reservation_id = reservation['id']
    #         name = reservation['name']
    #         phone = reservation['phone']
    #         adults = reservation['adults']
    #         children = reservation['children']
    #         check_in = reservation['check_in']
    #         check_out = reservation['check_out']
    #         price = reservation['price']
    #         room = Room.objects.get(pk=reservation['room'])
    #         try:
    #             Reservation.objects.update_or_create(external_id=reservation_id,
    #                                                  defaults={"room": room, "price": price, "name": name,
    #                                                            "phone": phone,
    #                                                            "adults": adults, "children": children,
    #                                                            "check_in": check_in, "check_out": check_out,
    #                                                            "confirm": True})
    #         except Exception as ex:
    #             pass
    #     self.message_user(request, 'Зареждане от Google Календар')
    #     return

    fieldsets = (
        ('', {
            'fields': ('confirm',)
        }),
        ('Резервация на:', {
            'fields': (
                'room', ('name', 'phone', 'email'), ('check_in', 'check_out'), ('adults', 'children'), 'description',
                ('price_currency', 'discount',),
                ('archived',))
        }),
    )


@admin.register(ArchivedReservation)
class ArchivedReservationAdmin(admin.ModelAdmin):
    list_display_links = ("title",)
    list_display = ("confirm", 'title', 'name', 'calc_days', 'check_in', 'check_out', 'added_on', 'price_currency')
    exclude = ('id',)

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(archived=True)

    fieldsets = (
        ('Резервация на:', {
            'fields': (
                'room', ('name', 'phone', 'email'), ('check_in', 'check_out'), ('adults', 'children'), 'description',
                ('price_currency', 'discount',))
        }),
    )


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('language',)
    inlines = (PageSectionInlineAdmin,)

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
    list_display = ('name', 'score', 'review_id')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @button(html_attrs={'style': 'background-color:#88FF88;color:black'})
    def load(self, request):
        self.message_user(request, 'Зареждане на съобщения от Booking.com')
        reviews, response = af.load_reviews()
        if response == 200:
            for review in reviews:
                review_id = review['review_id']
                name = review['author']['name']
                pros = review['pros']
                cons = review['cons']
                score_int = round(int(review['average_score']) * 1.25)
                score = '*' * score_int
                if not pros:
                    continue
                try:
                    Reviews.objects.create(review_id=review_id, name=name, pros=pros, cons=cons, score=score)
                except Exception as ex:
                    pass
        return

    fieldsets = (
        ('', {
            'fields': ('name', ('pros', 'cons'), 'score')
        }),
    )
