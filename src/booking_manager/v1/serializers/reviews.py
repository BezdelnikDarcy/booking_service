from rest_framework import serializers
from booking_manager.models import Reviews

class ReviewsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reviews
        fields = "__all__"
        read_only_fields = ("id","client")