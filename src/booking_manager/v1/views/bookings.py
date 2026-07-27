from booking_manager.models import Bookings
from booking_manager.v1.serializers.bookings import BookingSerializer
from rest_framework.exceptions import PermissionDenied
from rest_framework import status
from rest_framework.response import Response
from django.http import Http404
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated

from account.models.users import UserType


@extend_schema(tags=["Bookings"])
class BookingListApiView(APIView):
    serializer_class = BookingSerializer
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        summary="Получить список всех записей",
        description="Возвращает список всех записей",
        responses={200: BookingSerializer(many=True)},
    )
    def get(self, request):
        user = request.user

        if user.user_type == "admin":
            bookings = Bookings.objects.all()

        elif user.user_type == "employee":
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
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            if request.user.user_type == "client":
                serializer.save(client=request.user.client_profile)
            else:
                serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=["Bookings"])
class BookingDetailApiView(APIView):
    serializer_class = BookingSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self,request, pk):
        try:
            booking = Bookings.objects.get(pk=pk)
        except Bookings.DoesNotExist:
            raise Http404

        user = request.user

        if user.user_type == "admin":
            return booking

        if user.user_type == "employee" and booking.employee != user.employee_profile:
            raise Http404

        if user.user_type == "client" and booking.client != user.client_profile:
            raise Http404

        return booking

    @extend_schema(
        summary="Получить запись",
        description="Возвращает запись по идентификатору",
        responses={200: BookingSerializer},
    )
    def get(self, request, pk):
        booking = self.get_object(request,pk)
        serializer = BookingSerializer(booking)
        return Response(serializer.data)

    @extend_schema(
        summary="Изменить запись",
        description="Изменяет запись по идентификатору",
        request=BookingSerializer,
        responses={200: BookingSerializer},
    )
    def put(self, request, pk):
        self.check_edit_or_delete_client(request)
        booking = self.get_object(request, pk)
        serializer = BookingSerializer(booking, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Удалить запись",
        description="Удаляет запись по идентификатору",
        responses={204: None},
    )
    def delete(self, request, pk):
        self.check_edit_or_delete_client(request)
        booking = self.get_object(request, pk)
        booking.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def check_edit_or_delete_client(self, request):
        if request.user.user_type == UserType.CLIENT:
            raise PermissionDenied("Клиенты не могут изменять или удалять записи.")
