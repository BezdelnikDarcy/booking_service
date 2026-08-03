from rest_framework import serializers
from booking_manager.models import Notification

class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = "__all__"
        read_only_fields = ("id",)