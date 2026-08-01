from rest_framework import serializers
from booking_manager.models import Bookings
from booking_manager.services.booking_service import BookingService

from booking_manager.models import PromoCodes


class BookingSerializer(serializers.ModelSerializer):
    promo_code = serializers.PrimaryKeyRelatedField(
        queryset=PromoCodes.objects.all(),
        allow_null=True,
        required=False
    )

    rescheduled_from = serializers.PrimaryKeyRelatedField(
        queryset=Bookings.objects.all(),
        allow_null=True,
        required=False
    )

    class Meta:
        model = Bookings
        fields = "__all__"
        read_only_fields = ("id","client", "final_price", "total_price", "end_at")


    def create(self, validated_data):
        request = self.context["request"]
        return BookingService.create_booking(
            client=request.user.client_profile,
            **validated_data,
        )

