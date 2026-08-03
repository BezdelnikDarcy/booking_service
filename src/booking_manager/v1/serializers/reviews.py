from rest_framework import serializers
from booking_manager.models import Reviews
from booking_manager.services.reviews_service import ReviewsService


class ReviewsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reviews
        fields = "__all__"
        read_only_fields = ("id","client")



    def create(self, validated_data):
        request = self.context.get("request")

        return ReviewsService.create_reviews(
            client=request.user.client_profile,
            **validated_data
        )
