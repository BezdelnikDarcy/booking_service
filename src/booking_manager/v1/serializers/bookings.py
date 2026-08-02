from rest_framework import serializers
from booking_manager.models import Bookings
from booking_manager.services.booking_service import BookingService

from booking_manager.models import PromoCodes


class BookingSerializer(serializers.ModelSerializer):
    promo_code = serializers.CharField(
        allow_null=True,
        allow_blank=True,
        required=False,
        write_only=True,
    )

    rescheduled_from = serializers.PrimaryKeyRelatedField(
        queryset=Bookings.objects.all(),
        allow_null=True,
        required=False,
        read_only=True,
    )

    class Meta:
        model = Bookings
        fields = "__all__"
        read_only_fields = ("id","client", "final_price", "discount_amount", "total_price", "end_at")


    def create(self, validated_data):
        request = self.context["request"]

        promo_code = validated_data.pop("promo_code", None)

        return BookingService.create_booking(
            client=request.user.client_profile,
            promo_code=promo_code,
            **validated_data,
        )

class BookingRescheduleSerializer(serializers.Serializer):
    new_start_at = serializers.DateTimeField()