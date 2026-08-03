from rest_framework import serializers
from booking_manager.models import PromoUsage

class PromoUsageSerializer(serializers.ModelSerializer):

    class Meta:
        model = PromoUsage
        fields = "__all__"
        read_only_fields = ("id",)