from booking_manager.models import Categories
from booking_manager.v1.serializers.categories import CategorieSerializer
from rest_framework.exceptions import PermissionDenied, NotAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.http import Http404
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny

from account.models.users import UserType


@extend_schema(tags=["Categories"])
class CategoriesListApiView(APIView):
    serializer_class = CategorieSerializer
    permission_classes = (AllowAny,)

    @extend_schema(
        summary="Получить список всех категорий",
        description="Возвращает список всех категорий",
        responses={200: CategorieSerializer(many=True)},
    )
    def get(self, request):
        categories = Categories.objects.all()
        serializer = CategorieSerializer(categories, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Создать категорию",
        description="Создаёт категорию",
        request=CategorieSerializer,
        responses={201: CategorieSerializer},
    )
    def post(self, request):
        self.check_admin_permissions(request)

        serializer = CategorieSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def check_admin_permissions(self, request):
        if not request.user.is_authenticated:
            raise NotAuthenticated("Необходимо авторизоваться.")
        if not (request.user.is_superuser or request.user.user_type == UserType.ADMIN):
            raise PermissionDenied("Создать категории может только администратор.")


@extend_schema(tags=["Categories"])
class CategoriesDetailApiView(APIView):
    serializer_class = CategorieSerializer
    permission_classes = (AllowAny,)

    def get_object(self, pk):
        try:
            return Categories.objects.get(pk=pk)
        except Categories.DoesNotExist:
            raise Http404

    @extend_schema(
        summary="Получить категорию",
        description="Возвращает категорию по идентификатору",
        responses={200: CategorieSerializer},
    )
    def get(self, request,  pk):
        category = self.get_object(pk)
        serializer = CategorieSerializer(category)
        return Response(serializer.data)

    @extend_schema(
        summary="Изменить категорию",
        description="Изменяет категорию по идентификатору",
        request=CategorieSerializer,
        responses={200: CategorieSerializer},
    )
    def put(self, request, pk):
        self.check_admin_permissions(request)
        category = self.get_object(pk)
        serializer = CategorieSerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def check_admin_permissions(self, request):
        if not request.user.is_authenticated:
            raise NotAuthenticated("Необходимо авторизоваться.")
        if not (request.user.is_superuser or request.user.user_type == UserType.ADMIN):
            raise PermissionDenied("Изменять категорию может только администратор.")
