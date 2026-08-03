from rest_framework import serializers
from booking_manager.models import Services

class ServicesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Services
        fields = "__all__"
        read_only_fields = ("id",)