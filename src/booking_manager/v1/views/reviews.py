from booking_manager.models import Reviews
from booking_manager.v1.serializers.reviews import ReviewsSerializer
from rest_framework.exceptions import PermissionDenied
from rest_framework import status
from rest_framework.response import Response
from django.http import Http404
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from account.models.users import UserType



@extend_schema(tags=["Reviews"])
class ReviewListApiView(APIView):
    serializer_class = ReviewsSerializer
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        summary="Получить список отзывов",
        description="Возвращает список всех отзывов",
        responses={200: ReviewsSerializer(many=True)},
    )
    def get(self, request):
        if request.user.user_type != UserType.CLIENT :
            reviews = Reviews.objects.all()
        else:
            reviews = Reviews.objects.filter(is_moderated=True)
        serializer = ReviewsSerializer(reviews, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Создать отзыв",
        description="Создаёт отзыв",
        request=ReviewsSerializer,
        responses={201: ReviewsSerializer},
    )
    def post(self, request):
        if request.user.user_type != UserType.CLIENT :
            raise PermissionDenied("Отзывы могут оставлять только клиенты.")
        serializer = ReviewsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(client=request.user.client_profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Reviews"])
class ReviewDetailApiView(APIView):
    serializer_class = ReviewsSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self, pk):
        try:
            return Reviews.objects.get(pk=pk)
        except Reviews.DoesNotExist:
            raise Http404

    @extend_schema(
        summary="Получить отзыв",
        description="Возвращает отзыв по идентификатору",
        responses={200: ReviewsSerializer},
    )
    def get(self, request, pk):
        review = self.get_object(pk)
        if request.user.user_type == UserType.CLIENT and not review.is_moderated:
            raise Http404
        serializer = ReviewsSerializer(review)
        return Response(serializer.data)

    @extend_schema(
        summary="Изменить отзыв",
        description="Изменяет отзыв по идентификатору",
        request=ReviewsSerializer,
        responses={200: ReviewsSerializer},
    )
    def put(self, request, pk):
        review = self.get_object(pk)
        self.check_can_edit_review(request, review)

        serializer = ReviewsSerializer(review, data=request.data)
        if serializer.is_valid():
            serializer.save(client=request.user.client_profile)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Удалить отзыв",
        description="Удаляет отзыв по идентификатору",
        responses={204: None},
    )
    def delete(self, request, pk):
        review = self.get_object(pk)
        self.check_can_delete_review(request, review)
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def check_can_delete_review(self, request, review):
        if request.user.user_type == UserType.EMPLOYEE:
            raise PermissionDenied("Мастер не может удалять отзывы")
        if request.user.user_type == UserType.CLIENT and review.client != request.user.client_profile:
            raise PermissionDenied("Удалять можно только свой отзыв")

    def check_can_edit_review(self, request, review):
        if request.user.user_type != UserType.CLIENT:
            raise PermissionDenied("Изменять отзыв может только клиент")
        if review.client != request.user.client_profile:
            raise PermissionDenied("Изменять можно только свой отзыв")
        if review.is_moderated:
            raise PermissionDenied("Нельзя изменять модерированный отзыв")