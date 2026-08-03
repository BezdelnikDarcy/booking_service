from rest_framework import generics, mixins
from config.pagination import CustomUserPagination
from account.models import Users
from booking_manager.v1.serializers.users import UserSerializer
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from booking_manager.v1.filters.employee_users import EmployeeQueryFilter



@extend_schema(tags=['Users'])
class UserListApiView(
    mixins.ListModelMixin,
    generics.GenericAPIView,
):
    filter_backends = [DjangoFilterBackend,
                       filters.OrderingFilter,
    ]
    filterset_class = EmployeeQueryFilter
    permission_classes = (IsAdminUser,)
    queryset = (Users.objects
                .filter(is_active=True)
                .prefetch_related('employee_profile')
                .distinct()
    )
    serializer_class = UserSerializer
    pagination_class = CustomUserPagination

    ordering_fields = [
        "employee_profile__rating",
        "employee_profile__reviews_count",
        "employee_profile__experience_years",
    ]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
