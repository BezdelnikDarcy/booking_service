from rest_framework import generics, mixins
from config.pagination import CustomUserPagination
from account.models import Users
from booking_manager.v1.serializers.users import UserSerializer
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAdminUser


@extend_schema(tags=['Users'])
class UserListApiView(
    mixins.ListModelMixin,
    generics.GenericAPIView,
):
    permission_classes = (IsAdminUser,)
    queryset = Users.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomUserPagination

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
