from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import CustomUser, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_phone_number', 'get_role')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'profile__phone_number')

    def get_phone_number(self, obj):
        try:
            return obj.profile.phone_number
        except UserProfile.DoesNotExist:
            return '-'

    get_phone_number.short_description = 'Phone Number'

    def get_role(self, obj):
        groups = obj.groups.all()
        if groups:
            return ', '.join([group.name for group in groups])
        return 'No Role'

    get_role.short_description = 'Role'


admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'date_of_birth', 'created_at')
    list_filter = ('created_at', 'date_of_birth')
    search_fields = ('user__username', 'user__email', 'phone_number', 'address')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('User Information', {
            'fields': ('user', 'phone_number', 'profile_picture')
        }),
        ('Personal Details', {
            'fields': ('bio', 'date_of_birth', 'address')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
