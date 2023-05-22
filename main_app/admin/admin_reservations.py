from django.contrib import admin, messages
from datetime import datetime
from django.contrib.auth.models import Group
import hotel_gile.main_app.auxiliary_functions as af
from admin_extra_buttons.api import ExtraButtonsMixin, button
from hotel_gile.main_app.models import Reservation, ArchivedReservation, ReservedRooms, Room
import threading

admin.site.unregister(Group)


# ================ FUNCTIONS =====================


def get_content_type_for_model(obj):
    from django.contrib.contenttypes.models import ContentType
    return ContentType.objects.get_for_model(obj, for_concrete_model=False)


# ================================================


class ReservedRoomsInlineAdmin(admin.TabularInline):
    model = ReservedRooms
    extra = 0
    verbose_name = "стая"
    verbose_name_plural = "стаи"

    def get_formset(self, request, obj=None, **kwargs):
        form = super(ReservedRoomsInlineAdmin, self).get_formset(request, obj, **kwargs)
        room = form.form.base_fields["room"]
        room.widget.can_add_related = False
        room.widget.can_change_related = False
        room.widget.can_delete_related = False
        return form

    def get_min_num(self, request, obj=None, **kwargs):
        return 1

    def get_max_num(self, request, obj=None, **kwargs):
        return Room.objects.all().count()

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['admin_total_price', 'admin_price_per_night']
        return readonly_fields

    def get_fieldsets(self, request, obj=None):
        return (
            ('', {
                'fields': ('room', 'adults', 'children', 'discount', 'admin_price_per_night', 'admin_total_price')
            }),
        )


@admin.register(Reservation)
class ReservationAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    list_display_links = ('title_admin',)
    list_display = ('title_admin', 'name_admin', 'calc_days', 'check_in_admin', 'check_out_admin', 'added_on_admin',)
    search_fields = ['name__icontains', 'id__iexact']
    list_per_page = 15
    ordering = ['-new', 'check_in', 'check_out']
    inlines = (ReservedRoomsInlineAdmin,)

    @button(label='Препрати имейл',
            html_attrs={'style': 'background-color:#88FF88;color:black'})
    def resend_email(self, request, pk):
        obj = Reservation.objects.get(pk=pk)
        all_rooms = ReservedRooms.objects.filter(reservation=obj)

        if obj.status != 1:
            choices = obj.get_status_display.keywords['field'].choices
            self.message_user(request, f'Резервацията е {choices[obj.status][1].lower()}', level=messages.WARNING)
            return

        if not obj.email:
            self.message_user(request, f'Въведете валиден имейл адрес.', level=messages.WARNING)
            return

        if obj.email:
            response = af.send_confirmation_email(obj, list(all_rooms))
            if response:
                self.message_user(request, f'Успешно повторно изпращане на потвърдителен имейл: {obj.email}!',
                                  level=messages.SUCCESS)
            else:
                self.message_user(request, f'Неуспешно изпращане', level=messages.ERROR)
        return

    # ==============================================================================

    def get_queryset(self, request):
        return Reservation.objects.filter(check_out__gte=datetime.today())\
            .extra(select={'new': 'case when "status" = 0 then true else false end'})

    def get_search_results(self, request, queryset, search_term):
        search_term = search_term.lower()
        return super().get_search_results(request, queryset, search_term)

    @staticmethod
    def delete_reservation(reservations):
        for obj in reservations:
            if obj.external_id:
                try:
                    af.delete_reservation(obj)
                except Exception as ex:
                    print(ex)

    def delete_model(self, request, obj):
        if obj.email and obj.email_sent is False:
            threading.Thread(target=af.send_reject_email, args=obj).start()
        self.delete_reservation([obj])
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        self.delete_reservation(queryset)
        super().delete_queryset(request, queryset)

    def save_formset(self, request, form, formset, change):
        has_changed = True if any([x.has_changed() for x in formset]+[form.has_changed()]) else False
        super().save_formset(request, form, formset, change)
        if has_changed:
            all_rooms = sorted(set(list(formset.queryset) + formset.new_objects), key=lambda x: x.room_id)
            reservation = form.instance
            if reservation.status > 0:
                af.send_update_reservation(reservation, list(all_rooms))
                if reservation.email and reservation.email_sent is False:
                    threading.Thread(target=af.send_confirmation_email, args=(reservation, list(all_rooms))).start()
            else:
                self.delete_reservation([reservation])

    def log_change(self, request, obj, message):
        if message:
            return super().log_change(request, obj, message)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['price_currency', 'id']
        if obj and obj.status == 2:
            readonly_fields += ['status']
        return readonly_fields

    def get_fieldsets(self, request, obj=None):
        if obj:
            idn = obj.id
            obj.name = obj.name.title()
            return (
                (f'Резервация №: {idn}', {
                    'fields': ('status',
                               ('check_in', 'check_out'),
                               ('name', 'phone', 'email'),
                               'description',
                               ('price_currency',))
                }),
            )
        return (
            ('Нова резервация:', {
                'fields': ('status',
                           ('check_in', 'check_out'),
                           ('name', 'phone', 'email'),
                           'description',
                           ('price_currency',))
            }),
        )


@admin.register(ArchivedReservation)
class ArchivedReservationAdmin(admin.ModelAdmin):
    list_display_links = ("title",)
    list_display = ("title", 'name_admin', 'calc_days', 'check_in_admin', 'check_out_admin', 'added_on_admin',)
    search_fields = ['name__icontains', 'id__iexact', 'check_in__icontains', 'check_out__icontains']
    list_per_page = 15
    ordering = ('-check_in', '-check_out')
    exclude = ('id',)
    inlines = (ReservedRoomsInlineAdmin,)

    def history_view(self, request, object_id, extra_context=None):
        from django.template.response import TemplateResponse
        from django.contrib.admin.utils import unquote
        from django.contrib.admin.models import LogEntry
        from django.utils.text import capfirst

        obj = self.get_object(request, unquote(object_id))
        opts = obj._meta
        app_label = opts.app_label
        action_list = LogEntry.objects.filter(
            object_id=unquote(object_id),
            content_type=get_content_type_for_model(obj)
        ).select_related().order_by('action_time')

        context = dict(self.admin_site.each_context(request),
                       title='История на промените: %s' % obj,
                       action_list=action_list,
                       module_name=capfirst(opts.verbose_name_plural),
                       object=obj,
                       opts=opts,
                       preserved_filters=self.get_preserved_filters(request),
                       )
        context.update(extra_context or {})

        request.current_app = self.admin_site.name

        return TemplateResponse(request, self.object_history_template or [
            "admin/%s/%s/object_history.html" % (app_label, opts.model_name),
            "admin/%s/object_history.html" % app_label,
            "admin/object_history.html"
        ], context)

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

    def get_fieldsets(self, request, obj=None):
        obj.name = obj.name.title()
        return (
            (f'Резервация №: {obj.id}', {
                'fields': (
                    ('name', 'phone', 'email'), ('check_in_admin', 'check_out_admin'),
                    'description',
                    ('price_currency',))
            }),
        )
