from rest_framework import serializers
from account.models import Users

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Users
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "user_type",
        )
        read_only_fields = ('id',)