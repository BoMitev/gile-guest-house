from django.contrib import admin
from hotel_gile.main_app.models import Room, RoomPrice


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

    def log_change(self, request, obj, message):
        if message:
            return super().log_change(request, obj, message)

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
