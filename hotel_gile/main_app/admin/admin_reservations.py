from hotel_gile.main_app.functions import auxiliary_func as af
from hotel_gile.main_app.services import asi_payments, asi_email
from admin_extra_buttons.api import ExtraButtonsMixin, button, link
from pygments.formatters import HtmlFormatter
from django.utils import safestring
from django.contrib.auth.models import Group
from django.contrib import admin, messages
import hotel_gile.main_app.models as app_models
from pygments.lexers import JsonLexer
from datetime import datetime
from django.db import models
from pygments import highlight
import json

admin.site.unregister(Group)


class ReservedRoomsInlineAdmin(admin.TabularInline):
    model = app_models.ReservedRooms
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
        return app_models.Room.objects.all().count()

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['admin_total_price', 'admin_price_per_night']
        return readonly_fields

    def get_fieldsets(self, request, obj=None):
        return (
            ('', {
                'fields': ('room', 'adults', 'children', 'discount', 'admin_price_per_night', 'admin_total_price')
            }),
        )


@admin.register(app_models.PaymentLogs)
class PaymentLogsAdmin(admin.ModelAdmin):
    exclude = ('request_body', 'response_body')
    readonly_fields = ('requestBody', 'responseBody')
    list_display = ('reservation_id', 'method', 'code')

    def data_prettified(self, data):
        """Function to display pretty version of our data"""
        response = json.dumps(data, sort_keys=True, indent=2)
        response = response.encode('utf-8').decode('unicode_escape')
        formatter = HtmlFormatter()
        response = highlight(response, JsonLexer(), formatter)
        style = "<style>" + formatter.get_style_defs() + "</style>"
        return safestring.mark_safe(style + response)

    def requestBody(self, instance):
        return self.data_prettified(instance.request_body)
    requestBody.short_description = 'Request body'

    def responseBody(self, instance):
        return self.data_prettified(instance.response_body)
    responseBody.short_description = 'Response body'

    def has_delete_permission(self, request, obj=None):
        if request.user.id == 1:
            return True
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def get_fieldsets(self, request, obj=None):
        return (
            (f'Транзакция от {obj.created_at}', {
                'fields': (('host', 'method', 'code'),
                           ('reservation_url',),
                           ('requestBody', ),
                           ('responseBody',),)
            }),
        )


@admin.register(app_models.Reservation)
class ReservationAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    list_display_links = ('title_admin',)
    list_display = ('title_admin', 'name_admin', 'stay', 'check_in_admin', 'check_out_admin', 'added_on_admin',)
    search_fields = ['name__icontains', 'id__iexact', 'payment_id__iexact']
    list_per_page = 15
    inlines = (ReservedRoomsInlineAdmin,)

    @button(label='Провери плащане',
            html_attrs={'style': 'background-color:#e1b171;color:black'})
    def check_payment(self, request, pk):
        obj = self.get_object(request, pk)
        response, data = asi_payments.check_order_status(obj)

        if response:
            obj.save(has_changed=True)
            self.message_user(request, f'Резервацията е платена!', level=messages.SUCCESS)
        else:
            self.message_user(request, f'Няма плащане!', level=messages.WARNING)
        return

    @button(label='Създай линк за плащане',
            html_attrs={'style': 'background-color:#c44c10;color:black'})
    def create_payment_url(self, request, pk):
        obj = self.get_object(request, pk)
        if obj.status in [app_models.ReservationStatus.PENDING, app_models.ReservationStatus.ACCEPTED]:
            response, data = asi_payments.generate_payment_link(obj)

            if response:
                obj.save()
                self.message_user(request, f'Генериран нов линк за плащане', level=messages.SUCCESS)
            else:
                self.message_user(request, f'Грешка! {data}', level=messages.ERROR)
            return
        self.message_user(request, f'Резервацията е платена', level=messages.ERROR)
        return

    @button(label='Препрати имейл',
            html_attrs={'style': 'background-color:#88FF88;color:black'})
    def resend_email(self, request, pk):
        obj = self.get_object(request, pk)
        related_rooms = obj.reservedrooms_set.all()
        if obj.email:
            response = asi_email.send_confirmation_email(obj, related_rooms)
            if response is True:
                obj.save()
                self.message_user(request, f'Успешно повторно изпращане на потвърдителен имейл: {obj.email}!',
                                  level=messages.SUCCESS)
            else:
                self.message_user(request, f'Неуспешно изпращане.', level=messages.WARNING)
        else:
            self.message_user(request, f'Въведете валиден имейл адрес.', level=messages.WARNING)
        return

    # ==============================================================================

    def get_queryset(self, request):
        result = app_models.Reservation.objects.annotate(
            new=models.Case(
                models.When(status=0, then=True),
                default=False,
                output_field=models.BooleanField()
            )).filter(check_out__gte=datetime.today()).order_by('-new', 'check_in', 'check_out')
        return result

    def get_search_results(self, request, queryset, search_term):
        return super().get_search_results(request, queryset, search_term.lower())

    def delete_model(self, request, obj):
        if obj.email and obj.email_sent is False:
            asi_email.send_reject_email(obj)
        obj.__class__.unlink_reservations([obj])
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        if len(queryset) > 0:
            queryset[0].__class__.unlink_reservations(queryset)
        super().delete_queryset(request, queryset)

    def save_formset(self, request, form, formset, change):
        super().save_formset(request, form, formset, change)
        has_changed = True if any([x.has_changed() for x in formset] + [form.has_changed()]) else False
        form.instance.save(has_changed=has_changed)

    def log_change(self, request, obj, message):
        if message:
            return super().log_change(request, obj, message)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['price_currency', 'id']

        if obj and obj.status not in [app_models.ReservationStatus.PENDING, app_models.ReservationStatus.ACCEPTED]:
            if request.user.id != 1:
                readonly_fields += ['status']
        return readonly_fields

    def get_fieldsets(self, request, obj=None):
        if obj:
            # buttons visibility
            create_payment_url = False
            check_payment = False
            resend_email = False

            if request.user.is_superuser:
                create_payment_url = True
                check_payment = True
                resend_email = True

                if obj.status == app_models.ReservationStatus.PENDING:
                    resend_email = False

                if obj.status != app_models.ReservationStatus.ACCEPTED:
                    create_payment_url = False
                    check_payment = False

                if obj.payment_id is None:
                    check_payment = False

            self.extra_button_handlers['create_payment_url'].visible = create_payment_url
            self.extra_button_handlers['check_payment'].visible = check_payment
            self.extra_button_handlers['resend_email'].visible = resend_email
            ##################

            obj.name = obj.name.title()
            details = [
                f"Парола за достъп: {obj.locker_password}" if obj.locker_password_id else "",
            ]
            return (
                (f'Резервация №: {obj.id}{", ".join(details)}', {
                    'fields': (('status', 'generate_password'),
                               ('check_in', 'check_out'),
                               ('name', 'phone', 'email'),
                               'description',
                               ('price_currency',))
                }),
            )
        return (
            ('Нова резервация:', {
                'fields': (('status', 'generate_password'),
                           ('check_in', 'check_out'),
                           ('name', 'phone', 'email'),
                           'description',
                           ('price_currency',))
            }),
        )


@admin.register(app_models.ArchivedReservation)
class ArchivedReservationAdmin(admin.ModelAdmin):
    list_display_links = ("title",)
    list_display = ("title", 'name_admin', 'stay', 'check_in_admin', 'check_out_admin', 'added_on_admin',)
    search_fields = ['name__icontains', 'id__iexact', 'check_in__icontains', 'check_out__icontains']
    list_per_page = 15
    ordering = ('-check_in', '-check_out')
    exclude = ('id',)
    inlines = (ReservedRoomsInlineAdmin,)

    def history_view(self, request, object_id, extra_context=None):
        "The 'history' admin view for this model."
        from django.template.response import TemplateResponse
        from django.contrib.admin.views.main import PAGE_VAR
        from django.contrib.admin.utils import unquote
        from django.contrib.admin.models import LogEntry
        from django.utils.text import capfirst

        obj = self.get_object(request, unquote(object_id))
        opts = obj._meta
        model = opts.concrete_model

        if obj is None:
            return self._get_obj_does_not_exist_redirect(
                request, model._meta, object_id
            )

        app_label = opts.app_label
        action_list = (
            LogEntry.objects.filter(
                object_id=unquote(object_id),
                content_type=af.get_content_type_for_model(obj)
            )
            .select_related()
            .order_by('action_time')
        )

        paginator = self.get_paginator(request, action_list, 100)
        page_number = request.GET.get(PAGE_VAR, 1)
        page_obj = paginator.get_page(page_number)
        page_range = paginator.get_elided_page_range(page_obj.number)

        context = {
            **self.admin_site.each_context(request),
            "title": "История на промените: %s" % obj,
            "subtitle": None,
            "action_list": page_obj,
            "page_range": page_range,
            "page_var": PAGE_VAR,
            "pagination_required": paginator.count > 100,
            "module_name": str(capfirst(self.opts.verbose_name_plural)),
            "object": obj,
            "opts": self.opts,
            "preserved_filters": self.get_preserved_filters(request),
            **(extra_context or {}),
        }

        request.current_app = self.admin_site.name

        return TemplateResponse(
            request,
            self.object_history_template
            or [
                "admin/%s/%s/object_history.html" % (app_label, opts.model_name),
                "admin/%s/object_history.html" % app_label,
                "admin/object_history.html"
            ],
            context
        )

    def has_delete_permission(self, request, obj=None):
        if request.user.id == 1:
            return True
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        return app_models.Reservation.objects.filter(check_out__lt=datetime.today())

    def get_search_results(self, request, queryset, search_term):
        search_term = search_term.lower()
        return super().get_search_results(request, queryset, search_term)

    def get_fieldsets(self, request, obj=None):
        obj.name = obj.name.title()
        return (
            (f'Резервация №: {obj.id}', {
                'fields': (
                    ('name', 'phone_link', 'email_link'), ('check_in_admin', 'check_out_admin'),
                    'description',
                    ('price_currency',))
            }),
        )
