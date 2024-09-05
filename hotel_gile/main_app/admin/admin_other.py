from django.contrib import admin
from django.utils.html import format_html
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

    @button(html_attrs={'style': 'background-color:#88FF88;color:black'}, label='Зареждане на последните 20 отзива от Booking')
    def load(self, request):
        self.message_user(request, 'Успешно зареждане')
        self.model.bulk_create_with_limit()
        return

    fieldsets = (
        ('Отзив:', {
            'fields': ('name', 'pros', 'cons', 'score', 'date')
        }),
        ('От резервация:', {
            'fields': ('room', ('check_in', 'check_out'))
        }),
    )
