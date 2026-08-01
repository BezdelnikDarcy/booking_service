
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

class TestBookings(APITestCase):
    def setUp(self):
         self.client = APIClient()
         self.client_email ="test_client@test.com"
         self.client_phone = "12345"
         self.client_user = Users.objects.create_user(
             email=self.client_email,
             password="test",
             phone=self.client_phone,
            )
         self.master_email ="test_master@test.com"
         self.master_phone = "1234"
         self.employee_user = Users.objects.create_user(
            email=self.master_email,
            password="test",
            phone=self.master_phone,
            user_type = "employee",
         )

         self.category = Categories.objects.create(
            name = "test_category",
         )
         self.name_service = "test_name_service"
         self.service = Services.objects.create(
             name = self.name_service,
             category = self.category,
             status = "active",
         )
         self.price = 50
         self.duration = 40
         self.employee_service = EmployeeService.objects.create(
             employee = self.employee_user.employee_profile,
             service = self.service,
             price = self.price,
             duration = self.duration,
         )
         self.start_time_employee = time(10,00)
         self.end_time_employee = time(18,00)
         self.start_time_salon = time(8,00)
         self.end_time_salon = time(20,00)
         for weekday in range(7):
            SalonSchedule.objects.create(
                weekday=weekday,
                start_time=self.start_time_salon,
                end_time=self.end_time_salon,
            )
         self.start_at = timezone.make_aware(
            datetime(2026, 8, 7, 12, 0)
         )

         for weekday in range(7):
            EmployeeSchedule.objects.create(
               employee = self.employee_user.employee_profile,
               weekday = weekday,
               start_time =self.start_time_employee,
               end_time =self.end_time_employee,
            )





    def create_test_booking(self, start_at=None, client=None, employee_service=None):
        return BookingService.create_booking(
            client=client or self.client_user.client_profile,
            employee_service=employee_service or self.employee_service,
            start_at=start_at or self.start_at,
        )

    def test_create_booking_success(self):
        booking = self.create_test_booking()
        self.assertEqual(Bookings.objects.count(), 1)
        self.assertEqual(booking.client, self.client_user.client_profile)
        self.assertEqual(booking.employee_service, self.employee_service)

    def test_calculated_end_at(self):
        booking = self.create_test_booking()
        end_at = self.start_at + timedelta(minutes=self.duration)
        self.assertEqual(booking.end_at, end_at)

    def test_calculated_final_price(self):
        booking = self.create_test_booking()
        final_price = self.price - booking.discount_amount
        self.assertEqual(booking.final_price, final_price)

    def test_booking_in_past(self):
        past = timezone.make_aware(
            datetime(2026, 7, 24, 12, 0)
         )
        with self.assertRaises(ValidationError):
            self.create_test_booking(start_at=past)

    def test_booking_outside_working_hours_masters(self):
        not_working_time = timezone.make_aware(
            datetime(2026, 8, 7, 19, 0)
        )
        with self.assertRaises(ValidationError):
            self.create_test_booking(start_at=not_working_time)


    def test_booking_outside_working_hours_salon(self):
        not_working_time = timezone.make_aware(
            datetime(2026, 8, 7, 21, 0)
        )
        with self.assertRaises(ValidationError):
            self.create_test_booking(start_at=not_working_time)

    def test_booking_time_conflict_employee(self):
        self.create_test_booking()
        self.client_user_2 = Users.objects.create_user(
            email="test_client_2@test.com",
            password="test",
            phone="123452",
        )


        with self.assertRaises(ValidationError):
            self.create_test_booking(client=self.client_user_2.client_profile)



    def test_booking_time_conflict_client(self):
        self.create_test_booking()
        self.employee_user_2 = Users.objects.create_user(
            email="test_employee_2@test.com",
            password="test",
            phone="123452",
            user_type="employee",
        )
        self.employee_service_2 = EmployeeService.objects.create(
            employee=self.employee_user_2.employee_profile,
            service=self.service,
            price=self.price,
            duration=self.duration,
        )

        for weekday in range(7):
            EmployeeSchedule.objects.create(
                employee=self.employee_user_2.employee_profile,
                weekday=weekday,
                start_time=self.start_time_employee,
                end_time=self.end_time_employee,
            )
        with self.assertRaises(ValidationError):
            self.create_test_booking(employee_service=self.employee_service_2)

    def test_booking_on_employee_day_off(self):
        self.start_date_day_off = date(2026, 8, 11)
        self.end_date_day_off = date(2026, 8, 15)

        booking_date = timezone.make_aware(
            datetime(2026, 8, 13, 12, 0)
        )
        EmployeeDayOff.objects.create(
            employee = self.employee_user.employee_profile,
            start_date = self.start_date_day_off,
            end_date = self.end_date_day_off,
            reason = "test reason"
        )
        with self.assertRaises(ValidationError):
            self.create_test_booking(start_at=booking_date)



    def test_master_not_working(self):
        not_working_time = timezone.make_aware(
            datetime(2026, 8, 8, 12, 0)
        )
        EmployeeSchedule.objects.filter(
            employee = self.employee_user.employee_profile,
            weekday=5,
        ).update(is_working=False)
        with self.assertRaises(ValidationError):
            self.create_test_booking(start_at=not_working_time)