from django.contrib import admin
from .models import Event, Participant, Category, RSVP


@admin.register(RSVP)
class RSVPAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'event__category')
    search_fields = ('user__username', 'user__email', 'event__name')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'time', 'location', 'category', 'rsvp_count', 'image_preview')
    list_filter = ('date', 'category')
    search_fields = ('name', 'location', 'description')
    ordering = ('-date',)
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="max-height: 50px; max-width: 50px; object-fit: cover;" />'
        return "No Image"
    image_preview.short_description = 'Image Preview'
    image_preview.allow_tags = True


admin.site.register(Participant)
admin.site.register(Category)
