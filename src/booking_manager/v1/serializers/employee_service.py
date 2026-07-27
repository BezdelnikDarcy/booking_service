from rest_framework import serializers
from booking_manager.models import EmployeeService

class EmployeeServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmployeeService
        fields = "__all__"
        read_only_fields = ("id",)