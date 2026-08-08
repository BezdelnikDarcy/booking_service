import factory

from account.models.users import Users, UserType

TEST_PASSWORD = 'test'

class ClientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Users

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Sequence(lambda n: f"user{n}@test.com")
    phone = factory.Sequence(lambda n: f"37544{n}")
    password = factory.PostGenerationMethodCall(
        "set_password",
        TEST_PASSWORD,
    )


class EmployeeFactory(ClientFactory):
    user_type = UserType.EMPLOYEE


class AdminFactory(ClientFactory):
    user_type = UserType.ADMIN