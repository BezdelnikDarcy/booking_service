from rest_framework import serializers
from booking_manager.models import EmployeeDayOff

class EmployeeDayOffSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmployeeDayOff
        fields = "__all__"
        read_only_fields = ("id",)