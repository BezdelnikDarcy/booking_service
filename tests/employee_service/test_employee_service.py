
from datetime import time, datetime, date, timedelta
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from rest_framework.test import APITestCase, APIClient
from account.models.users import Users
from django.urls import reverse
from booking_manager.models.bookings import Bookings
from booking_manager.models.categories import Categories
from booking_manager.models.services import Services
from booking_manager.models.employee_service import EmployeeService
from booking_manager.models.salon_schedule import SalonSchedule
from booking_manager.models.employee_schedule import EmployeeSchedule
from booking_manager.models import EmployeeDayOff
from booking_manager.services.booking_service import BookingService
from booking_manager.services.employee_schedule_service import EmployeeScheduleService
from booking_manager.services.employee_day_off_service import EmployeeDayOffService

from account.models.users import UserType
from rest_framework import status

from booking_manager.constants import ServiceStatus


class TestAdminEmployeeServiceAPI(APITestCase):
    def setUp(self):
         self.client = APIClient()

         self.admin_email ="test_admin@test.com"
         self.admin_phone = "1234"
         self.admin_user = Users.objects.create_user(
            email=self.admin_email,
            password="test",
            phone=self.admin_phone,
            user_type = UserType.ADMIN,
         )
         token_url = reverse('token_obtain_pair')
         response = self.client.post(token_url, data={
             'email': self.admin_email,
             'password': 'test',
         })
         self.access_token = response.data['access']

         self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.access_token}")


         self.employee_email ="test_employee@test.com"
         self.employee_phone = "12345"


         self.category = Categories.objects.create(
            name = "test_category",
         )
         self.name_service = "test_name_service"
         self.price = 50
         self.duration = 40

    def create_service(self, name, category):
        return Services.objects.create(
            name = name,
            status = ServiceStatus.ACTIVE,
            category = category,
        )

    def create_employee(self, email, phone, first_name=None):
        return Users.objects.create_user(
             email=email,
             password="test",
             phone=phone,
             first_name=first_name,
             user_type = UserType.EMPLOYEE,
            )


    def create_employee_service(self, employee, service, price, duration):
        return EmployeeService.objects.create(
            employee = employee,
            service = service,
            price = price,
            duration = duration,
        )




    #Тест создание услуги мастера, я опустил момент создания категории и самой услуги
    def test_create_employee_service_success(self):
        employee = self.create_employee(self.employee_email, self.employee_phone)
        service = self.create_service(self.name_service, self.category)


        employee_service_create_url = reverse('employee-services')
        data = {
            'employee': employee.employee_profile.id,
            'service': service.id,
            'price': self.price,
            'duration': self.duration,
        }
        response = self.client.post(employee_service_create_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(EmployeeService.objects.count(), 1)

    #Тест изменение услуги мастера
    def test_update_employee_service_success(self):
        employee = self.create_employee(self.employee_email, self.employee_phone)
        service = self.create_service(self.name_service, self.category)

        employee_service = self.create_employee_service(employee.employee_profile, service, price=self.price, duration=self.duration)
        employee_service_update_url = reverse('employee-service', args=[employee_service.id])
        data = {
            'employee': employee.employee_profile.id,
            'service': service.id,
            'price': 70,
            'duration': 35,
        }

        response = self.client.put(employee_service_update_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        employee_service.refresh_from_db()
        self.assertEqual(EmployeeService.objects.count(), 1)
        self.assertEqual(employee_service.price, Decimal("70.00"))
        self.assertEqual(employee_service.duration, 35)


    #Тест на фильтрацию по мастеру или услуге
    def test_filter_employee_service(self):
        service = self.create_service(self.name_service, self.category)
        for num in range(15):
            employee = self.create_employee(email=f"test_employee_{num}@test.com", phone=int(f"123455{num}"))
            self.create_employee_service(employee=employee.employee_profile, service=service, price=self.price+10*num, duration=self.duration+5*num)

        employee_service_filter_url = reverse('employee-services')
        data = {
            'price__min': 80,
            'price__max': 120,
            'duration__min': 40,
            'duration__max': 65,
        }
        #всего лишь 3 пересечения данного фильтра, проверим статус код и кол-во пересечений
        response = self.client.get(employee_service_filter_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 3)


    def test_search_employee_service(self):
        service = self.create_service(self.name_service, self.category)
        for num in range(15):
            employee = self.create_employee(email=f"test_employee_{num}@test.com", phone=f"123455{num}", first_name=f"employee_{num}")
            self.create_employee_service(employee=employee.employee_profile, service=service, price=self.price+10*num, duration=self.duration+5*num)

        employee_service_filter_url = reverse('employee-services')
        data = {"search": "oyee_1"}
        response = self.client.get(employee_service_filter_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 6)


    #Проверка пагинации
    def test_paginate_employee_service(self):
        service = self.create_service(self.name_service, self.category)
        for num in range(15):
            employee = self.create_employee(email=f"test_employee_{num}@test.com", phone=int(f"123455{num}"))
            self.create_employee_service(employee=employee.employee_profile, service=service, price=self.price+num, duration=self.duration+num)

        employee_service_filter_url = reverse('employee-services')
        #Первая страница(по дефолту 10 записей)
        response = self.client.get(employee_service_filter_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверка кол-во записей на стринице
        self.assertEqual(len(response.data['results']), 10)
        #Проверка общего кол-во записей
        self.assertEqual(response.data['count'], 15)
        #Проверка, что страница "next" существует
        self.assertIsNotNone(response.data['next'])
        #Проверка, что преведущей записи нет
        self.assertIsNone(response.data['previous'])


        #Проверка второй страницы (offset = 10
        response = self.client.get(employee_service_filter_url, {"offset": 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверка кол-во записей на стринице
        self.assertEqual(len(response.data['results']), 5)
        #Проверка, что следующей записи нет
        self.assertIsNone(response.data['next'])
        # Проверка, что страница "previous" существует
        self.assertIsNotNone(response.data['previous'])


    def test_not_valid_price(self):
        service = self.create_service(self.name_service, self.category)
        employee = self.create_employee(
            email=self.employee_email,
            phone=self.employee_phone,
            first_name="employee"
        )
        employee_service_create_url = reverse('employee-services')
        data = {
            'employee': employee.employee_profile.id,
            'service': service.id,
            'price': -10,
            'duration': self.duration,
        }

        response = self.client.post(employee_service_create_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(EmployeeService.objects.count(), 0)



    def test_not_valid_duration(self):
        service = self.create_service(self.name_service, self.category)
        employee = self.create_employee(
            email=self.employee_email,
            phone=self.employee_phone,
            first_name="employee"
        )
        employee_service_create_url = reverse('employee-services')
        data = {
            'employee': employee.employee_profile.id,
            'service': service.id,
            'price': self.price,
            'duration': 3,
        }

        response = self.client.post(employee_service_create_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(EmployeeService.objects.count(), 0)


    def test_not_valid_id_service(self):
        employee = self.create_employee(
            email=self.employee_email,
            phone=self.employee_phone,
            first_name="employee"
        )
        employee_service_create_url = reverse('employee-services')
        data = {
            'employee': employee.employee_profile.id,
            'service': 777,
            'price': self.price,
            'duration': self.duration,
        }

        response = self.client.post(employee_service_create_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(EmployeeService.objects.count(), 0)


class TestClientEmployeeServiceAPI(APITestCase):
    def setUp(self):
         self.client = APIClient()

         self.email ="test_client_user@test.com"
         self.phone = "89543123"
         self.client_user = Users.objects.create_user(
            email=self.email,
            password="test",
            phone=self.phone,
         )
         token_url = reverse('token_obtain_pair')
         response = self.client.post(token_url, data={
             'email': self.email,
             'password': 'test',
         })
         self.access_token = response.data['access']

         self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.access_token}")

         self.category = Categories.objects.create(
            name = "test_category",
         )
         self.name_service = "test_name_service"
         self.price = 50
         self.duration = 40


         self.service_name = "test_service"
         self.service = Services.objects.create(
             name=self.service_name,
             status=ServiceStatus.ACTIVE,
             category=self.category,
         )
         self.employee_email ="test_employee_user@test.com"
         self.employee_phone = "45321"
         self.employee_user = Users.objects.create_user(
             email=self.employee_email,
             password="test",
             phone=self.employee_phone,
             user_type=UserType.EMPLOYEE,
         )

         self.employee_service = EmployeeService.objects.create(
             employee=self.employee_user.employee_profile,
             service=self.service,
             price=self.price,
             duration=self.duration,
         )


    #Тест создания услуги мастера без прав доступа
    def test_user_create_employee_service(self):
        employee_service_create_url = reverse('employee-services')
        data = {
            'employee': self.employee_user.id,
            'service': self.service.id,
            'price': self.price,
            'duration': self.duration,
        }
        response = self.client.post(employee_service_create_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        #Проверяем, что не добавилось услуг, помимо услуги созданой в setUp
        self.assertEqual(EmployeeService.objects.count(), 1)


    #Тест создание услуги мастера неавторизованым пользователем
    def test_unauthorized_create_employee_service(self):
        self.client.credentials(user=None)
        employee_service_create_url = reverse('employee-services')
        data = {
            'employee': self.employee_user.id,
            'service': self.service.id,
            'price': self.price,
            'duration': self.duration,
        }
        response = self.client.post(employee_service_create_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        #Проверяем, что не добавилось услуг, помимо услуги созданой в setUp
        self.assertEqual(EmployeeService.objects.count(), 1)

    #Тест получения несуществующей записи
    def test_get_employee_service_not_found(self):
        employee_service_get_detail_url = reverse('employee-service', args=[888])
        response = self.client.get(employee_service_get_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    #Тест получения информации об услугах мастеров неавторизованым пользователем
    def test_unauthorized_get_all_employee_services(self):
        self.client.credentials(user=None)
        employee_service_get_url = reverse('employee-services')
        response = self.client.get(employee_service_get_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    #Тест получения существующей услуги неавторизованым пользователем
    def test_unauthorized_get_employee_service_detail(self):
        self.client.credentials(user=None)
        employee_service_detail_get_url = reverse('employee-service', args=[self.employee_service.id])
        response = self.client.get(employee_service_detail_get_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.employee_service.id)

    def test_unauthorized_put_employee_service(self):

        self.client.credentials(user=None)
        employee_service_detail_put_url = reverse('employee-service', args=[self.employee_service.id])
        data = {
            'employee': self.employee_user.employee_profile.id,
            'service': self.service.id,
            'price': 70,
            'duration': 35,
        }
        response = self.client.put(employee_service_detail_put_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.employee_service.refresh_from_db()
        self.assertEqual(self.employee_service.price, Decimal(self.price))
        self.assertEqual(self.employee_service.duration, self.duration)


    def test_client_put_employee_service(self):

        employee_service_detail_put_url = reverse('employee-service', args=[self.employee_service.id])
        data = {
            'employee': self.employee_user.employee_profile.id,
            'service': self.service.id,
            'price': 70,
            'duration': 35,
        }
        response = self.client.put(employee_service_detail_put_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.employee_service.refresh_from_db()
        self.assertEqual(self.employee_service.price, Decimal(self.price))
        self.assertEqual(self.employee_service.duration, self.duration)
