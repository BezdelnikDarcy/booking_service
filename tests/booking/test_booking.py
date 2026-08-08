
from datetime import time, datetime, date, timedelta
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.test import TestCase, Client
from booking_manager.models.bookings import Bookings
from booking_manager.models.salon_schedule import SalonSchedule
from booking_manager.models.employee_schedule import EmployeeSchedule
from booking_manager.models import EmployeeDayOff
from booking_manager.services.booking_service import BookingService
from booking_manager.services.employee_schedule_service import EmployeeScheduleService
from booking_manager.services.employee_day_off_service import EmployeeDayOffService
from booking_manager.constants import ServiceStatus
from tests.factories.services import ServicesFactory, EmployeeServicesFactory, TEST_SERVICE_DURATION, TEST_SERVICE_PRICE
from tests.factories.users import ClientFactory, EmployeeFactory




class TestBookings(TestCase):
    def setUp(self):
         self.client = Client()
         self.client_user = ClientFactory()
         self.employee_user = EmployeeFactory()
         self.service = ServicesFactory()
         self.employee_service = EmployeeServicesFactory(
             service=self.service,
             employee=self.employee_user.employee_profile,
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
            datetime(2026, 8, 14, 12, 0)
         )

         for weekday in range(7):
            EmployeeScheduleService.create_employee_schedule(
               employee = self.employee_user.employee_profile,
               weekday = weekday,
               start_time =self.start_time_employee,
               end_time =self.end_time_employee,
            )




    #Функция создания записи(что бы не дублировать в каждом тесте)
    def create_test_booking(
            self,
            start_at=None,
            client=None,
            employee_service=None
    ):
        return BookingService.create_booking(
            client=client or self.client_user.client_profile,
            employee_service=employee_service or self.employee_service,
            start_at=start_at or self.start_at,
        )

    #Проверяем что запись создалась и получаем данные которые ожидаем получить
    def test_create_booking_success(self):
        booking = self.create_test_booking()
        self.assertEqual(Bookings.objects.count(), 1)
        self.assertEqual(booking.client, self.client_user.client_profile)
        self.assertEqual(booking.employee_service, self.employee_service)

    #Тест проверки автоматического расчёта времени окончания услуги
    def test_calculated_end_at(self):
        booking = self.create_test_booking()
        end_at = self.start_at + timedelta(minutes=TEST_SERVICE_DURATION)
        self.assertEqual(booking.end_at, end_at)

    #Тест расчёта финальной стоимости услуги с учётом скидки
    def test_calculated_final_price(self):
        booking = self.create_test_booking()
        final_price = TEST_SERVICE_PRICE - booking.discount_amount
        self.assertEqual(booking.final_price, final_price)

    #Тест создания записи в прошлом
    def test_booking_in_past(self):
        past = timezone.make_aware(
            datetime(2026, 7, 24, 12, 0)
         )
        with self.assertRaises(ValidationError):
            self.create_test_booking(start_at=past)
        self.assertEqual(Bookings.objects.count(), 0)

    #Тест создания записи в нерабочее время мастера
    def test_booking_outside_working_hours_masters(self):
        not_working_time = timezone.make_aware(
            datetime(2026, 8, 14, 19, 0)
        )
        with self.assertRaises(ValidationError):
            self.create_test_booking(start_at=not_working_time)
        self.assertEqual(Bookings.objects.count(), 0)

    #Тест создания записи в нерабочее время салона
    def test_booking_outside_working_hours_salon(self):
        not_working_time = timezone.make_aware(
            datetime(2026, 8, 7, 21, 0)
        )
        with self.assertRaises(ValidationError):
            self.create_test_booking(start_at=not_working_time)
        self.assertEqual(Bookings.objects.count(), 0)

    #Тест конфликта уремени у мастера(когда 2 пользователя хотят записаться на одну и ту же услугу)
    def test_booking_time_conflict_employee(self):
        self.create_test_booking()
        self.client_user_2 = ClientFactory()

        with self.assertRaises(ValidationError):
            self.create_test_booking(client=self.client_user_2.client_profile)
        self.assertEqual(Bookings.objects.count(), 1)

    #Тест конфликта времени при записи одним клиентом на разные услуги
    def test_booking_time_conflict_client(self):
        self.create_test_booking()
        self.employee_user_2 = EmployeeFactory()
        self.employee_service_2 = EmployeeServicesFactory(employee=self.employee_user_2.employee_profile)

        for weekday in range(7):
            EmployeeScheduleService.create_employee_schedule(
                employee=self.employee_user_2.employee_profile,
                weekday=weekday,
                start_time=self.start_time_employee,
                end_time=self.end_time_employee,
            )
        with self.assertRaises(ValidationError):
            self.create_test_booking(employee_service=self.employee_service_2)
        self.assertEqual(Bookings.objects.count(), 1)


    #Тест создания записи в выходной день мастера
    def test_booking_on_employee_day_off(self):
        self.start_date_day_off = date(2026, 8, 11)
        self.end_date_day_off = date(2026, 8, 15)


        EmployeeDayOffService.create_employee_days_off(
            employee = self.employee_user.employee_profile,
            start_date = self.start_date_day_off,
            end_date = self.end_date_day_off,
            reason = "test reason"
        )
        with self.assertRaises(ValidationError):
            self.create_test_booking(start_at=self.start_at)
        self.assertEqual(Bookings.objects.count(), 0)


    #Тест создания записи в нерабочи день мастера
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
        self.assertEqual(Bookings.objects.count(), 0)

    #Тест создания записи на неактивную услугу салона
    def test_service_inactive(self):
        self.service.status = ServiceStatus.INACTIVE
        with self.assertRaises(ValidationError):
            self.create_test_booking()
        self.assertEqual(Bookings.objects.count(), 0)

    #Тест создания записи на архивированую услугу салона
    def test_service_archived(self):
        self.service.status = ServiceStatus.ARCHIVED
        with self.assertRaises(ValidationError):
            self.create_test_booking()
        self.assertEqual(Bookings.objects.count(), 0)

    #Тест создания записи на неактивную услугу мастера
    def test_employee_service_not_active(self):
        self.employee_service.is_active = False
        with self.assertRaises(ValidationError):
            self.create_test_booking()
        self.assertEqual(Bookings.objects.count(), 0)
