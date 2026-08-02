import django_filters
from account.models import Users



class EmployeeQueryFilter(django_filters.FilterSet):
    service = django_filters.NumberFilter(field_name='service__category_id'    )
    rating_min = django_filters.NumberFilter(field_name='employee_profile__rating', lookup_expr='gte')
    reviews_count_min = django_filters.NumberFilter(field_name='employee_profile__reviews_count', lookup_expr='gte')


    class Meta:
        model = Users
        fields = []

