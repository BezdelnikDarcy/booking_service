from django import forms
from django.contrib import admin
from booking_manager.models import Services, Categories, Bookings, Reviews, EmployeeService, PromoCodes, PromoUsage, Notification, EmployeeDayOff, EmployeeSchedule, SalonSchedule
from django.contrib.admin.widgets import AdminTimeWidget


@admin.register(Services)
class ServiceAdmin(admin.ModelAdmin):
    fields = (
        ("name", "category", "status"),
        "description",
        "image",
    )
    list_display = (
        "name",
        "category",
        "status",
    )
    list_filter = (
        "category",
        "status",
    )
    search_fields = (
        "name",
        "description",
    )
    list_editable = ("status",)
    list_per_page = 20

    ordering = ("name",)

@admin.register(Bookings)
class BookingAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None,
            {
                "fields": ["employee_service", "client", "status", "start_at", "end_at","promo_code", "total_price", "discount_amount", "final_price", "client_notes"],
            },
        ),
        (
            "Дополнительная информация",
            {
                "classes": ["collapse"],
                "fields": ["cancellation_reason", "cancelled_at", "rescheduled_from", "reminder_sent", "reminder_sent_at"],
            },
        ),
    ]
    list_display = (
        "employee_service",
        "client",
        "status",
        "start_at",
        "final_price"
    )
    list_filter = ("start_at",
                   "status"
                   )
    search_fields = (
        "employee_service",
        "client",
    )
    list_editable = ("status",)
    list_per_page = 20
    readonly_fields = ("discount_amount", "final_price", "total_price" )
    ordering = ("start_at",)


class DayOffForm(forms.ModelForm):
    class Meta:
        model = EmployeeDayOff
        fields = '__all__'
        widgets = {
            'start_date': forms.TimeInput(attrs={'type': 'date',}),
            'end_date': forms.TimeInput(attrs={'type': 'date',}),
        }

@admin.register(EmployeeDayOff)
class DayOffAdmin(admin.ModelAdmin):
    form = DayOffForm
    list_display = ('id', 'employee', 'start_date', 'end_date', 'reason')
    list_filter = ('employee',)
    search_fields = ('employee__user__email',)
    ordering = ('employee', 'start_date', 'end_date')



# admin.site.register(Services)
admin.site.register(Categories)
# admin.site.register(Bookings)
admin.site.register(Reviews)
admin.site.register(EmployeeService)
admin.site.register(PromoCodes)
admin.site.register(PromoUsage)
admin.site.register(Notification)
# admin.site.register(EmployeeDayOff)
admin.site.register(EmployeeSchedule)
admin.site.register(SalonSchedule)


# Register your models here.
class CustomAdminTimeWidget(AdminTimeWidget):
    def __init__(self, attrs=None):
        default_attrs = {'step': '3600'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)








