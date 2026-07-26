from django.contrib import admin
from django.contrib.auth.hashers import make_password
from account.models.users import Users, ClientProfile

@admin.register(Users)
class UserAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if 'password' in form.changed_data:
            obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)

