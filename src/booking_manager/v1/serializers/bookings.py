from rest_framework import serializers
from booking_manager.models import Bookings

class BookingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bookings
        fields = "__all__"
        read_only_fields = ("id","client")