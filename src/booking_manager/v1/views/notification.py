from booking_manager.models import Notification
from booking_manager.v1.serializers.notification import NotificationSerializer
from rest_framework import status
from rest_framework.response import Response
from django.http import Http404
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAdminUser


@extend_schema(tags=["Notification"])
class NotificationListApiView(APIView):
    serializer_class = NotificationSerializer
    permission_classes = (IsAdminUser,)

    @extend_schema(
        summary="Получить список всех уведомлений",
        description="Возвращает список всех уведомлений",
        responses={200: NotificationSerializer(many=True)},
    )
    def get(self, request):
        notification = Notification.objects.all()
        serializer = NotificationSerializer(notification, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Notification"])
class NotificationDetailApiView(APIView):
    serializer_class = NotificationSerializer
    permission_classes = (IsAdminUser,)

    def get_object(self, pk):
        try:
            return Notification.objects.get(pk=pk)
        except Notification.DoesNotExist:
            raise Http404

    @extend_schema(
        summary="Получить уведомление",
        description="Возвращает уведомление по идентификатору",
        responses={200: NotificationSerializer},
    )
    def get(self, request,  pk):
        notification = self.get_object(pk)
        serializer = NotificationSerializer(notification)
        return Response(serializer.data)



