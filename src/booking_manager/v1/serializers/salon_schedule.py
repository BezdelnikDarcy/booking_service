from rest_framework import serializers
from booking_manager.models import SalonSchedule

class SalonScheduleSerializer(serializers.ModelSerializer):

    class Meta:
        model = SalonSchedule
        fields = "__all__"
        read_only_fields = ("id",)