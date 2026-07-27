from booking_manager.models import EmployeeSchedule
from booking_manager.v1.serializers.employee_schedule import EmployeeScheduleSerializer
from rest_framework.exceptions import PermissionDenied
from rest_framework import status
from rest_framework.response import Response
from django.http import Http404
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from account.models.users import UserType



@extend_schema(tags=["EmployeeSchedule"])
class EmployeeScheduleListApiView(APIView):
    serializer_class = EmployeeScheduleSerializer

    @extend_schema(
        summary="Получить расписание всех мастеров",
        description="Возвращает расписание всех мастеров",
        responses={200: EmployeeScheduleSerializer(many=True)},
    )
    def get(self, request):
        if request.user.user_type != UserType.CLIENT :
            employee_schedule = EmployeeSchedule.objects.all()
        else:
            employee_schedule = EmployeeSchedule.objects.filter(is_working=True)
        serializer = EmployeeScheduleSerializer(employee_schedule, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Создать расписание мастера",
        description="Создаёт расписание мастера",
        request=EmployeeScheduleSerializer,
        responses={201: EmployeeScheduleSerializer},
    )
    def post(self, request):
        self.check_admin_permissions(request)

        serializer = EmployeeScheduleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def check_admin_permissions(self, request):
        if not (request.user.is_superuser or request.user.user_type == UserType.ADMIN):
            raise PermissionDenied("Создать расписание может только администратор.")


@extend_schema(tags=["EmployeeSchedule"])
class EmployeeScheduleDetailApiView(APIView):
    serializer_class = EmployeeScheduleSerializer

    def get_object(self, pk):
        try:
            return EmployeeSchedule.objects.get(pk=pk)
        except EmployeeSchedule.DoesNotExist:
            raise Http404

    @extend_schema(
        summary="Получить расписание рабочего дня мастера",
        description="Возвращает расписание рабочего дня мастера по идентификатору",
        responses={200: EmployeeScheduleSerializer},
    )
    def get(self, request, pk):
        employee_schedule = self.get_object(pk)
        if request.user.user_type == UserType.CLIENT and not employee_schedule.is_working:
            raise Http404
        serializer = EmployeeScheduleSerializer(employee_schedule)
        return Response(serializer.data)

    @extend_schema(
        summary="Изменить расписание рабочего дня мастера",
        description="Изменяет расписание рабочего дня мастера по идентификатору",
        request=EmployeeScheduleSerializer,
        responses={200: EmployeeScheduleSerializer},
    )
    def put(self, request, pk):
        self.check_admin_permissions(request)
        employee_schedule = self.get_object(pk)
        serializer = EmployeeScheduleSerializer(employee_schedule, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def check_admin_permissions(self, request):
        if not (request.user.is_superuser or request.user.user_type == UserType.ADMIN):
            raise PermissionDenied("Изменять расписание мастера может только администратор.")
