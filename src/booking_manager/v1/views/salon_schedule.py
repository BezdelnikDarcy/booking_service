from booking_manager.models import SalonSchedule
from booking_manager.v1.serializers.salon_schedule import SalonScheduleSerializer
from rest_framework.exceptions import PermissionDenied, NotAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.http import Http404
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from account.models.users import UserType



@extend_schema(tags=["SalonSchedule"])
class SalonScheduleListApiView(APIView):
    serializer_class = SalonScheduleSerializer
    permission_classes = (AllowAny,)

    @extend_schema(
        summary="Получить список всех рабочих дней салона",
        description="Возвращает список всех рабочих дней салона",
        responses={200: SalonScheduleSerializer(many=True)},
    )
    def get(self, request):
        if request.user.is_authenticated and request.user.user_type != UserType.CLIENT:
            salon_schedule = SalonSchedule.objects.all()
        else:
            salon_schedule = SalonSchedule.objects.filter(is_working=True)
        serializer = SalonScheduleSerializer(salon_schedule, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Создать расписание на рабочий день",
        description="Создаёт расписание на рабочий день",
        request=SalonScheduleSerializer,
        responses={201: SalonScheduleSerializer},
    )
    def post(self, request):
        self.check_admin_permissions(request)

        serializer = SalonScheduleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def check_admin_permissions(self, request):
        if not request.user.is_authenticated:
            raise NotAuthenticated("Необходимо авторизоваться.")
        if not (request.user.is_superuser or request.user.user_type == UserType.ADMIN):
            raise PermissionDenied("Создать расписание может только администратор.")


@extend_schema(tags=["SalonSchedule"])
class SalonScheduleDetailApiView(APIView):
    serializer_class = SalonScheduleSerializer
    permission_classes = (AllowAny,)

    def get_object(self, pk):
        try:
            return SalonSchedule.objects.get(pk=pk)
        except SalonSchedule.DoesNotExist:
            raise Http404

    @extend_schema(
        summary="Получить рабочий день",
        description="Возвращает рабочий день по идентификатору",
        responses={200: SalonScheduleSerializer},
    )
    def get(self, request, pk):
        salon_schedule = self.get_object(pk)
        if not salon_schedule.is_working:
            if not request.user.is_authenticated or request.user.user_type == UserType.CLIENT:
                raise Http404
        serializer = SalonScheduleSerializer(salon_schedule)
        return Response(serializer.data)

    @extend_schema(
        summary="Изменить расписание рабочего дня",
        description="Изменяет расписание рабочего дня по идентификатору",
        request=SalonScheduleSerializer,
        responses={200: SalonScheduleSerializer},
    )
    def put(self, request, pk):
        self.check_admin_permissions(request)
        salon_schedule = self.get_object(pk)
        serializer = SalonScheduleSerializer(salon_schedule, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Удалить расписание рабочего дня",
        description="Удаляет расписание рабочего дня по идентификатору",
        responses={204: None},
    )
    def delete(self, request, pk):
        self.check_admin_permissions(request)
        salon_schedule = self.get_object(pk)
        salon_schedule.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def check_admin_permissions(self, request):
        if not request.user.is_authenticated:
            raise NotAuthenticated("Необходимо авторизоваться.")
        if not (request.user.is_superuser or request.user.user_type == UserType.ADMIN):
            raise PermissionDenied("Изменять или удалять расписание может только администратор.")
