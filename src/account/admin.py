from django.contrib import admin
from django.contrib.auth.hashers import make_password
from account.models.users import Users, ClientProfile, EmployeeProfile, AdminProfile

@admin.register(Users)
class UserAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if 'password' in form.changed_data:
            obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'specialization',
        'rating',
        'reviews_count',
        'experience_years',
        'is_available',
        'is_verified',
        'is_active',
    )
    list_filter = (
        'is_available',
        'is_verified',
        'is_active',
        'specialization',
    )
    search_fields = (
        'user__email',
        'user__first_name',
        'user__last_name',
        'specialization',
    )
    readonly_fields = ('rating', 'reviews_count')
    fieldsets = (
        ('Основное', {
            'fields': ('user', 'specialization', 'experience_years', 'photo')
        }),
        ('Рейтинг', {
            'fields': ('rating', 'reviews_count')
        }),
        ('Статусы', {
            'fields': ('is_available', 'is_verified', 'is_active')
        }),
        ('Настройки', {
            'fields': ('work_time_hours', 'timezone_offset')
        }),
    )
