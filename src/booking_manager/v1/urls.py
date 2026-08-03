from django.urls import path
from booking_manager.v1.views.bookings import (
    BookingListApiView,
    BookingDetailApiView,
    BookingMarkNoShowApiView,
    BookingCompleteApiView,
    BookingCancelApiView,
    BookingRescheduleApiView,
)
from booking_manager.v1.views.categories import CategoriesListApiView, CategoriesDetailApiView
from booking_manager.v1.views.employee_day_off import EmployeeDayOffListApiView, EmployeeDayOffDetailApiView
from booking_manager.v1.views.employee_schedule import EmployeeScheduleListApiView, EmployeeScheduleDetailApiView
from booking_manager.v1.views.employee_service import EmployeeServiceListApiView, EmployeeServiceDetailApiView
from booking_manager.v1.views.notification import NotificationListApiView, NotificationDetailApiView
from booking_manager.v1.views.promo_usage import PromoUsageListApiView, PromoUsageDetailApiView
from booking_manager.v1.views.promocodes import PromoCodesListApiView, PromoCodesDetailApiView
from booking_manager.v1.views.reviews import ReviewListApiView, ReviewDetailApiView
from booking_manager.v1.views.salon_schedule import SalonScheduleListApiView, SalonScheduleDetailApiView
from booking_manager.v1.views.services import ServiceListApiView, ServiceDetailApiView

from booking_manager.v1.views.users import UserListApiView

urlpatterns = [
    path("bookings/", BookingListApiView.as_view(), name="bookings-list"),
    path("booking/<int:pk>/", BookingDetailApiView.as_view(), name="booking"),
    path("booking/<int:pk>/mark-no-show/", BookingMarkNoShowApiView.as_view(), name="booking-mark-no-show"),
    path("booking/<int:pk>/complete/", BookingCompleteApiView.as_view(), name="booking-complete"),
    path("booking/<int:pk>/cancel/", BookingCancelApiView.as_view(), name="booking-cancel"),
    path("booking/<int:pk>/reschedule/", BookingRescheduleApiView.as_view(), name="booking-reschedule"),
    path("categories/", CategoriesListApiView.as_view(), name="categories"),
    path("category/<int:pk>/", CategoriesDetailApiView.as_view(), name="category-detail"),
    path("employee-days-off/", EmployeeDayOffListApiView.as_view(), name="employee-days-off"),
    path("employee-day-off/<int:pk>/", EmployeeDayOffDetailApiView.as_view(), name="employee-day-off"),
    path("employee-schedules/", EmployeeScheduleListApiView.as_view(), name="employee-schedules"),
    path("employee-schedule/<int:pk>/", EmployeeScheduleDetailApiView.as_view(), name="employee-schedule"),
    path("employee-services/", EmployeeServiceListApiView.as_view(), name="employee-services"),
    path("employee-service/<int:pk>/", EmployeeServiceDetailApiView.as_view(), name="employee-service"),
    path("notifications/", NotificationListApiView.as_view(), name="notifications"),
    path("notification/<int:pk>/", NotificationDetailApiView.as_view(), name="notification"),
    path("promo-usages/", PromoUsageListApiView.as_view(), name="promo-usages"),
    path("promo-usage/<int:pk>/", PromoUsageDetailApiView.as_view(), name="promo-usage"),
    path("promo-codes/", PromoCodesListApiView.as_view(), name="promo-codes"),
    path("promo-code/<int:pk>/", PromoCodesDetailApiView.as_view(), name="promo-code"),
    path("reviews/", ReviewListApiView.as_view(), name="reviews"),
    path("review/<int:pk>/", ReviewDetailApiView.as_view(), name="review"),
    path("salon-schedules/", SalonScheduleListApiView.as_view(), name="salon-schedules"),
    path("salon-schedule/<int:pk>/", SalonScheduleDetailApiView.as_view(), name="salon-schedule"),
    path("services/", ServiceListApiView.as_view(), name="services"),
    path("service/<int:pk>/", ServiceDetailApiView.as_view(), name="service"),
    path("users/", UserListApiView.as_view(), name="users"),

]