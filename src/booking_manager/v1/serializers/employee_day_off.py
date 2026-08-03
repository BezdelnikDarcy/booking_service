from rest_framework import serializers
from booking_manager.models import EmployeeDayOff

from booking_manager.services.employee_day_off_service import EmployeeDayOffService


class EmployeeDayOffSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmployeeDayOff
        fields = "__all__"
        read_only_fields = ("id",)



    def create(self, validated_data):
        request = self.context.get("request")

        return EmployeeDayOffService.create_employee_days_off(
            employee=request.user.employee_profile,
            **validated_data,
        )