import django_filters
from account.models import Users



class EmployeeQueryFilter(django_filters.FilterSet):
    service = django_filters.NumberFilter(field_name='employee_profile__employee_services__service_id')
    rating_min = django_filters.NumberFilter(field_name='employee_profile__rating', lookup_expr='gte')
    rating_max = django_filters.NumberFilter(field_name='employee_profile__rating', lookup_expr='lte')
    reviews_count_min = django_filters.NumberFilter(field_name='employee_profile__reviews_count', lookup_expr='gte')
    reviews_count_max = django_filters.NumberFilter(field_name='employee_profile__reviews_count', lookup_expr='lte')
    experience_years_min = django_filters.NumberFilter(field_name='employee_profile__experience_years', lookup_expr='gte')
    experience_years_max = django_filters.NumberFilter(field_name='employee_profile__experience_years', lookup_expr='lte')


    class Meta:
        model = Users
        fields = []

