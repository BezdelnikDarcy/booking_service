from booking_manager.models import EmployeeService
from booking_manager.v1.serializers.employee_service import EmployeeServiceSerializer
from rest_framework.exceptions import PermissionDenied, NotAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.http import Http404
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from account.models.users import UserType



@extend_schema(tags=["EmployeeService"])
class EmployeeServiceListApiView(APIView):
    serializer_class = EmployeeServiceSerializer
    permission_classes = (AllowAny,)

    @extend_schema(
        summary="Получить список всех услуг мастеров",
        description="Возвращает список всех услуг мастеров",
        responses={200: EmployeeServiceSerializer(many=True)},
    )
    def get(self, request):
        if request.user.is_authenticated and request.user.user_type != UserType.CLIENT :
            employee_service = EmployeeService.objects.all()
        else:
            employee_service = EmployeeService.objects.filter(is_active=True)
        serializer = EmployeeServiceSerializer(employee_service, many=True)
        return Response(serializer.data)

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
