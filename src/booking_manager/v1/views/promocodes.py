from booking_manager.models import PromoCodes
from booking_manager.v1.serializers.promocodes import PromoCodesSerializer
from rest_framework import status
from rest_framework.response import Response
from django.http import Http404
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAdminUser


@extend_schema(tags=["PromoCodes"])
class PromoCodesListApiView(APIView):
    serializer_class = PromoCodesSerializer
    permission_classes = (IsAdminUser,)

    @extend_schema(
        summary="Получить список всех промокодов",
        description="Возвращает список всех промокодов",
        responses={200: PromoCodesSerializer(many=True)},
    )
    def get(self, request):
        promo_codes = PromoCodes.objects.all()
        serializer = PromoCodesSerializer(promo_codes, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Создать промокод",
        description="Создаёт промокод",
        request=PromoCodesSerializer,
        responses={201: PromoCodesSerializer},
    )
    def post(self, request):

        serializer = PromoCodesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["PromoCodes"])
class PromoCodesDetailApiView(APIView):
    serializer_class = PromoCodesSerializer
    permission_classes = (IsAdminUser,)

    def get_object(self, pk):
        try:
            return PromoCodes.objects.get(pk=pk)
        except PromoCodes.DoesNotExist:
            raise Http404

    @extend_schema(
        summary="Получить промокод",
        description="Возвращает промокод по идентификатору",
        responses={200: PromoCodesSerializer},
    )
    def get(self, request,  pk):
        promo_code = self.get_object(pk)
        serializer = PromoCodesSerializer(promo_code)
        return Response(serializer.data)

    @extend_schema(
        summary="Изменить промокод",
        description="Изменяет промокод по идентификатору",
        request=PromoCodesSerializer,
        responses={200: PromoCodesSerializer},
    )
    def put(self, request, pk):
        promo_code = self.get_object(pk)
        serializer = PromoCodesSerializer(promo_code, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


