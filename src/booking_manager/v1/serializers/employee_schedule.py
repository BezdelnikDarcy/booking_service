from rest_framework import serializers
from booking_manager.models import EmployeeSchedule

class EmployeeScheduleSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmployeeSchedule
        fields = "__all__"
        read_only_fields = ("id",)