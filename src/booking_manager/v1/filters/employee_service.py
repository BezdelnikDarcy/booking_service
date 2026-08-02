import django_filters
from booking_manager.models import EmployeeService
from booking_manager.models import Categories


class EmployeeServiceQueryFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(field_name='service__category_id'    )
    price__min = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price__max = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    duration__min = django_filters.NumberFilter(field_name='duration', lookup_expr='gte')
    duration__max = django_filters.NumberFilter(field_name='duration', lookup_expr='lte')

    class Meta:
        model = EmployeeService
        fields = ['category']
