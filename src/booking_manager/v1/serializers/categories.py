from rest_framework import serializers
from booking_manager.models import Categories

class CategorieSerializer(serializers.ModelSerializer):

    class Meta:
        model = Categories
        fields = "__all__"
        read_only_fields = ("id",)