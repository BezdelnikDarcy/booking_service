from booking_manager.models import PromoUsage
from booking_manager.v1.serializers.promo_usage import PromoUsageSerializer
from rest_framework.response import Response
from django.http import Http404
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAdminUser


@extend_schema(tags=["PromoUsage"])
class PromoUsageListApiView(APIView):
    serializer_class = PromoUsageSerializer
    permission_classes = (IsAdminUser,)

    @extend_schema(
        summary="Получить список всех использований промокодов",
        description="Возвращает список всех использований промокодов",
        responses={200: PromoUsageSerializer(many=True)},
    )
    def get(self, request):
        promo_usage = PromoUsage.objects.all()
        serializer = PromoUsageSerializer(promo_usage, many=True)
        return Response(serializer.data)


@extend_schema(tags=["PromoUsage"])
class PromoUsageDetailApiView(APIView):
    serializer_class = PromoUsageSerializer
    permission_classes = (IsAdminUser,)

    def get_object(self, pk):
        try:
            return PromoUsage.objects.get(pk=pk)
        except PromoUsage.DoesNotExist:
            raise Http404

    @extend_schema(
        summary="Получить историю использования промокода",
        description="Возвращает историю использования промокода по идентификатору",
        responses={200: PromoUsageSerializer},
    )
    def get(self, request,  pk):
        promo_usage = self.get_object(pk)
        serializer = PromoUsageSerializer(promo_usage)
        return Response(serializer.data)

