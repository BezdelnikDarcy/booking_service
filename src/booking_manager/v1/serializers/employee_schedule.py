from rest_framework import serializers
from booking_manager.models import EmployeeSchedule
from booking_manager.services.employee_schedule_service import EmployeeScheduleService

class EmployeeScheduleSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmployeeSchedule
        fields = "__all__"
        read_only_fields = ("id",)



    def create(self, validated_data):
        request = self.context.get("request")

        return EmployeeScheduleService.create_employee_schedule(
            employee=request.user.employee_profile,
            **validated_data,
        )