import factory

from booking_manager.models.services import Services
from booking_manager.models.categories import Categories
from booking_manager.models.employee_service import EmployeeService
from booking_manager.constants import ServiceStatus
from tests.factories.users import EmployeeFactory


#Объединил фабрики категории, услуг и услуг мастеров, т.к. в большинстве тестов они вызываются вместе, а так же удобнее
TEST_SERVICE_PRICE = 50
TEST_SERVICE_DURATION = 40



class CategoriesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Categories

    name = factory.Sequence(lambda n: f"Category {n}")


class ServicesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Services

    name = factory.Sequence(lambda n: f"Service {n}")
    status=ServiceStatus.ACTIVE
    category=factory.SubFactory(CategoriesFactory)


class EmployeeServicesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EmployeeService

    employee = factory.SubFactory(EmployeeFactory)
    service = factory.SubFactory(ServicesFactory)
    price = TEST_SERVICE_PRICE
    duration = TEST_SERVICE_DURATION
