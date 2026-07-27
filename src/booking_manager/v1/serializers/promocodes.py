from rest_framework import serializers
from booking_manager.models import PromoCodes

class PromoCodesSerializer(serializers.ModelSerializer):

    class Meta:
        model = PromoCodes
        fields = "__all__"
        read_only_fields = ("id",)