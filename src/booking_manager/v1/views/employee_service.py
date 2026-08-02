from rest_framework import filters
from rest_framework import generics
from booking_manager.models import EmployeeService
from booking_manager.v1.serializers.employee_service import EmployeeServiceSerializer
from booking_manager.v1.filters.employee_service import EmployeeServiceQueryFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import PermissionDenied, NotAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.http import Http404
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from account.models.users import UserType



@extend_schema(tags=["EmployeeService"])
class EmployeeServiceListApiView(generics.ListCreateAPIView):
    filter_backends = [DjangoFilterBackend,
                       filters.OrderingFilter,
                       filters.SearchFilter,]
    filterset_class = EmployeeServiceQueryFilter
    serializer_class = EmployeeServiceSerializer
    permission_classes = (AllowAny,)
    search_fields = [
        "service__name",
        "employee__user__first_name",
    ]
    ordering_fields = [
        "price",
        "duration",
    ]

    queryset = EmployeeService.objects.filter(is_active=True).select_related('service__category')

    @extend_schema(
        summary="Создать услугу мастера",
        description="Создаёт услугу мастера",
        request=EmployeeServiceSerializer,
        responses={201: EmployeeServiceSerializer},
    )
    def post(self, request):
        self.check_admin_permissions(request)

        serializer = EmployeeServiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def check_admin_permissions(self, request):
        if not request.user.is_authenticated:
            raise NotAuthenticated("Необходимо авторизоваться.")
        if not (request.user.is_superuser or request.user.user_type == UserType.ADMIN):
            raise PermissionDenied("Создать услуги мастера может только администратор.")


@extend_schema(tags=["EmployeeService"])
class EmployeeServiceDetailApiView(APIView):
    serializer_class = EmployeeServiceSerializer
    permission_classes = (AllowAny,)

    def get_object(self, pk):
        try:
            return EmployeeService.objects.get(pk=pk)
        except EmployeeService.DoesNotExist:
            raise Http404

    @extend_schema(
        summary="Получить услугу мастера",
        description="Возвращает услугу мастера по идентификатору",
        responses={200: EmployeeServiceSerializer},
    )
    def get(self, request, pk):
        employee_service = self.get_object(pk)
        if not employee_service.is_active:
            if not request.user.is_authenticated or request.user.user_type == UserType.CLIENT:
                raise Http404
        serializer = EmployeeServiceSerializer(employee_service)
        return Response(serializer.data)

    @extend_schema(
        summary="Изменить услугу мастера",
        description="Изменяет услугу мастера по идентификатору",
        request=EmployeeServiceSerializer,
        responses={200: EmployeeServiceSerializer},
    )
    def put(self, request, pk):
        self.check_admin_permissions(request)
        employee_service = self.get_object(pk)
        serializer = EmployeeServiceSerializer(employee_service, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def check_admin_permissions(self, request):
        if not request.user.is_authenticated:
            raise NotAuthenticated("Необходимо авторизоваться.")
        if not (request.user.is_superuser or request.user.user_type == UserType.ADMIN):
            raise PermissionDenied("Изменять услуги мастера может только администратор.")
