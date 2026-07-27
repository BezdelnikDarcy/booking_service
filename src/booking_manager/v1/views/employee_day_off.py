from django.utils import timezone

from booking_manager.models import EmployeeDayOff
from booking_manager.v1.serializers.employee_day_off import EmployeeDayOffSerializer
from rest_framework.exceptions import PermissionDenied
from rest_framework import status
from rest_framework.response import Response
from django.http import Http404
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from account.models.users import UserType



@extend_schema(tags=["EmployeeDayOff"])
class EmployeeDayOffListApiView(APIView):
    serializer_class = EmployeeDayOffSerializer

    @extend_schema(
        summary="Получить расписание всех активных выходных мастеров",
        description="Возвращает расписание всех активных выходных мастеров",
        responses={200: EmployeeDayOffSerializer(many=True)},
    )
    def get(self, request):
        self.check_staff_permissions(request)
        today = timezone.now().date()
        if request.user.user_type == UserType.ADMIN:
            employee_day_off = EmployeeDayOff.objects.filter(end_date__gte=today)
        else:
            employee_day_off = EmployeeDayOff.objects.filter(
                employee=request.user.employee_profile,
                end_date__gte=today,
            )
        serializer = EmployeeDayOffSerializer(employee_day_off, many=True)
        return Response(serializer.data)


    @extend_schema(
        summary="Создать выходной мастера",
        description="Создаёт выходной мастера",
        request=EmployeeDayOffSerializer,
        responses={201: EmployeeDayOffSerializer},
    )
    def post(self, request):
        self.check_admin_permissions(request)

        serializer = EmployeeDayOffSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def check_admin_permissions(self, request):
        if not (request.user.is_superuser or request.user.user_type == UserType.ADMIN):
            raise PermissionDenied("Создать расписание выходных может только администратор.")
    def check_staff_permissions(self, request):
        if request.user.user_type == UserType.CLIENT:
            raise PermissionDenied("Информация доступна только для работников")

@extend_schema(tags=["EmployeeDayOff"])
class EmployeeDayOffDetailApiView(APIView):
    serializer_class = EmployeeDayOffSerializer

    def get_object(self, pk):
        try:
            return EmployeeDayOff.objects.get(pk=pk)
        except EmployeeDayOff.DoesNotExist:
            raise Http404

    @extend_schema(
        summary="Получить расписание выходного мастера",
        description="Возвращает расписание выходного мастера по идентификатору",
        responses={200: EmployeeDayOffSerializer},
    )
    def get(self, request, pk):
        self.check_staff_permissions(request)
        employee_day_off = self.get_object(pk)
        if request.user.user_type == UserType.EMPLOYEE and employee_day_off.employee != request.user.employee_profile:
            raise PermissionDenied("Можно просматривать только свои выходные.")
        serializer = EmployeeDayOffSerializer(employee_day_off)
        return Response(serializer.data)

    @extend_schema(
        summary="Изменить расписание выходного дня мастера",
        description="Изменяет расписание выходного дня мастера по идентификатору",
        request=EmployeeDayOffSerializer,
        responses={200: EmployeeDayOffSerializer},
    )
    def put(self, request, pk):
        self.check_admin_permissions(request)
        employee_day_off = self.get_object(pk)
        serializer = EmployeeDayOffSerializer(employee_day_off, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def check_admin_permissions(self, request):
        if not (request.user.is_superuser or request.user.user_type == UserType.ADMIN):
            raise PermissionDenied("Изменять расписание выходного дня мастера может только администратор.")
    def check_staff_permissions(self, request):
        if request.user.user_type == UserType.CLIENT:
            raise PermissionDenied("Информация доступна только для работников")