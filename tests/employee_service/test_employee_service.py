
from datetime import time, datetime, date, timedelta
from django.core.exceptions import ValidationError
from django.utils import timezone
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


class TestEmployeeServiceAPI(APITestCase):
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

    def create_services(self, name, category):
        return Services.objects.create(
            name = name,
            status = ServiceStatus.ACTIVE,
            category = category,
        )

    def create_employee_users(self, email, phone, first_name=None):
        return Users.objects.create_user(
             email=email,
             password="test",
             phone=phone,
            first_name=first_name,
             user_type = UserType.EMPLOYEE,
            )


    def create_employee_services(self, employee, service, price, duration):
        return EmployeeService.objects.create(
            employee = employee,
            service = service,
            price = price,
            duration = duration,
        )




    #Тест создание услуги мастера, я опустил момент создания категории и самой услуги
    def test_create_employee_success(self):
        employee = self.create_employee_users(self.employee_email, self.employee_phone)
        service = self.create_services(self.name_service, self.category)


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


    #Тест на фильтрацию по мастеру или услуге
    def test_filter_employee_service(self):
        service = self.create_services(self.name_service, self.category)
        for num in range(15):
            employee = self.create_employee_users(email=f"test_employee_{num}@test.com", phone=int(f"123455{num}"))
            self.create_employee_services(employee=employee.employee_profile, service=service, price=self.price+10*num, duration=self.duration+5*num)

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
        service = self.create_services(self.name_service, self.category)
        for num in range(15):
            employee = self.create_employee_users(email=f"test_employee_{num}@test.com", phone=int(f"123455{num}"), first_name=f"employee_{num}")
            self.create_employee_services(employee=employee.employee_profile, service=service, price=self.price+10*num, duration=self.duration+5*num)

        employee_service_filter_url = reverse('employee-services')
        data = {"search": "oyee_1"}
        response = self.client.get(employee_service_filter_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 6)


    #Проверка пагинации
    def test_paginate_employee_service(self):
        service = self.create_services(self.name_service, self.category)
        for num in range(15):
            employee = self.create_employee_users(email=f"test_employee_{num}@test.com", phone=int(f"123455{num}"))
            self.create_employee_services(employee=employee.employee_profile, service=service, price=self.price+num, duration=self.duration+num)

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