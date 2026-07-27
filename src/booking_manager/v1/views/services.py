from booking_manager.models import Services
from booking_manager.v1.serializers.services import ServicesSerializer
from rest_framework.exceptions import PermissionDenied
from rest_framework import status
from rest_framework.response import Response
from django.http import Http404
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from booking_manager.constants import ServiceStatus
from account.models.users import UserType



@extend_schema(tags=["Services"])
class ServiceListApiView(APIView):
    serializer_class = ServicesSerializer
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        summary="Получить список всех услуг",
        description="Возвращает список всех услуг",
        responses={200: ServicesSerializer(many=True)},
    )
    def get(self, request):
        if request.user.user_type != UserType.CLIENT :
            services = Services.objects.all()
        else:
            services = Services.objects.filter(status=ServiceStatus.ACTIVE)
        serializer = ServicesSerializer(services, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Создать услугу",
        description="Создаёт услугу",
        request=ServicesSerializer,
        responses={201: ServicesSerializer},
    )
    def post(self, request):
        self.check_admin_permissions(request)

        serializer = ServicesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def check_admin_permissions(self, request):
        if request.user.user_type != UserType.ADMIN:
            raise PermissionDenied("Создать услуги может только администратор.")


@extend_schema(tags=["Services"])
class ServiceDetailApiView(APIView):
    serializer_class = ServicesSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self, pk):
        try:
            return Services.objects.get(pk=pk)
        except Services.DoesNotExist:
            raise Http404

    @extend_schema(
        summary="Получить услугу",
        description="Возвращает услугу по идентификатору",
        responses={200: ServicesSerializer},
    )
    def get(self, request, pk):
        service = self.get_object(pk)
        if request.user.user_type == UserType.CLIENT and service.status != ServiceStatus.ACTIVE:
            raise Http404
        serializer = ServicesSerializer(service)
        return Response(serializer.data)

    @extend_schema(
        summary="Изменить услугу",
        description="Изменяет услугу по идентификатору",
        request=ServicesSerializer,
        responses={200: ServicesSerializer},
    )
    def put(self, request, pk):
        self.check_admin_permissions(request)
        service = self.get_object(pk)
        serializer = ServicesSerializer(service, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def check_admin_permissions(self, request):
        if request.user.user_type != UserType.ADMIN:
            raise PermissionDenied("Изменять услуги может только администратор.")
