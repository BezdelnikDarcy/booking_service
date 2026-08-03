from booking_manager.models import Bookings
from booking_manager.v1.serializers.bookings import BookingSerializer, BookingRescheduleSerializer
from rest_framework.exceptions import PermissionDenied
from rest_framework import status
from rest_framework.response import Response
from django.http import Http404
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from account.models.users import UserType
from booking_manager.services.booking_service import BookingService



class BookingActionBaseView(APIView):
    def get_object(self,request, pk):
        try:
            booking = Bookings.objects.get(pk=pk)
        except Bookings.DoesNotExist:
            raise Http404

        user = request.user

        if user.is_superuser or user.user_type == UserType.ADMIN:
            return booking

        if user.user_type == UserType.EMPLOYEE and booking.employee != user.employee_profile:
            raise Http404

        if user.user_type == UserType.CLIENT and booking.client != user.client_profile:
            raise Http404

        return booking


    def check_employee_or_admin(self, request):
        if request.user.user_type == UserType.CLIENT:
            raise PermissionDenied("Клиенты не могут изменять записи.")

@extend_schema(tags=["Bookings"])
class BookingListApiView(APIView):
    serializer_class = BookingSerializer

    @extend_schema(
        summary="Получить список всех записей",
        description="Возвращает список всех записей",
        responses={200: BookingSerializer(many=True)},
    )
    def get(self, request):
        user = request.user

        if user.is_superuser or user.user_type == UserType.ADMIN:
            bookings = Bookings.objects.all()

        elif user.user_type == UserType.EMPLOYEE:
            bookings = Bookings.objects.filter(
                employee_service__employee=user.employee_profile
            )

        else:
            bookings = Bookings.objects.filter(
                client=user.client_profile
            )
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Создать запись",
        description="Создаёт запись",
        request=BookingSerializer,
        responses={201: BookingSerializer},
    )
    def post(self, request):
        serializer = BookingSerializer(
            data=request.data,
            context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=["Bookings"])
class BookingDetailApiView(BookingActionBaseView):
    serializer_class = BookingSerializer


    @extend_schema(
        summary="Получить запись",
        description="Возвращает запись по идентификатору",
        responses={200: BookingSerializer},
    )
    def get(self, request, pk):
        booking = self.get_object(request,pk)
        serializer = BookingSerializer(booking)
        return Response(serializer.data)



@extend_schema(tags=["Bookings"])
class BookingMarkNoShowApiView(BookingActionBaseView):
    serializer_class = BookingSerializer

    @extend_schema(
        summary="Поставить неявку по записи",
        description="Ставит неявку на запись по идентификатору",
        request=BookingSerializer,
        responses={200: BookingSerializer},
    )
    def post(self, request, pk):
        self.check_employee_or_admin(request)
        booking = self.get_object(request, pk)
        booking = BookingService.mark_no_show(booking)
        serializer = BookingSerializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)





@extend_schema(tags=["Bookings"])
class BookingCompleteApiView(BookingActionBaseView):
    serializer_class = BookingSerializer

    @extend_schema(
        summary="Завершает запись",
        description="Завершает запись по идентификатору",
        request=BookingSerializer,
        responses={200: BookingSerializer},
    )
    def post(self, request, pk):
        self.check_employee_or_admin(request)
        booking = self.get_object(request, pk)
        booking = BookingService.complete_booking(booking)
        serializer = BookingSerializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)



@extend_schema(tags=["Bookings"])
class BookingCancelApiView(BookingActionBaseView):
    serializer_class = BookingSerializer


    @extend_schema(
        summary="Отменяет запись",
        description="Отменяет запись по идентификатору",
        request=BookingSerializer,
        responses={200: BookingSerializer},
    )
    def post(self, request, pk):
        self.check_employee_or_admin(request)
        booking = self.get_object(request, pk)
        booking = BookingService.cancel_booking(booking, reason=request.data.get("reason"))
        serializer = BookingSerializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)

@extend_schema(tags=["Bookings"])
class BookingRescheduleApiView(BookingActionBaseView):
    serializer_class = BookingRescheduleSerializer

    @extend_schema(
        summary="Переносит запись",
        description="Переносит запись по идентификатору",
        request=BookingSerializer,
        responses={200: BookingSerializer},
    )
    def post(self, request, pk):
        self.check_employee_or_admin(request)
        booking = self.get_object(request, pk)
        serializer = BookingRescheduleSerializer(data=request.data)
        if serializer.is_valid():
            new_booking = BookingService.reschedule_booking(booking,
                                              serializer.validated_data["new_start_at"],
                                              )
            return Response(BookingSerializer(new_booking).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



