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
    path("booking/<int:pk>/", BookingDetailApiView.as_view()),
    path("booking/<int:pk>/mark-no-show/", BookingMarkNoShowApiView.as_view()),
    path("booking/<int:pk>/complete/", BookingCompleteApiView.as_view()),
    path("booking/<int:pk>/cancel/", BookingCancelApiView.as_view()),
    path("booking/<int:pk>/reschedule/", BookingRescheduleApiView.as_view()),
    path("categories/", CategoriesListApiView.as_view()),
    path("category/<int:pk>/", CategoriesDetailApiView.as_view()),
    path("employee-days-off/", EmployeeDayOffListApiView.as_view()),
    path("employee-day-off/<int:pk>/", EmployeeDayOffDetailApiView.as_view()),
    path("employee-schedules/", EmployeeScheduleListApiView.as_view()),
    path("employee-schedule/<int:pk>/", EmployeeScheduleDetailApiView.as_view()),
    path("employee-services/", EmployeeServiceListApiView.as_view()),
    path("employee-service/<int:pk>/", EmployeeServiceDetailApiView.as_view()),
    path("notifications/", NotificationListApiView.as_view()),
    path("notification/<int:pk>/", NotificationDetailApiView.as_view()),
    path("promo-usages/", PromoUsageListApiView.as_view()),
    path("promo-usage/<int:pk>/", PromoUsageDetailApiView.as_view()),
    path("promo-codes/", PromoCodesListApiView.as_view()),
    path("promo-code/<int:pk>/", PromoCodesDetailApiView.as_view()),
    path("reviews/", ReviewListApiView.as_view()),
    path("review/<int:pk>/", ReviewDetailApiView.as_view()),
    path("salon-schedules/", SalonScheduleListApiView.as_view()),
    path("salon-schedule/<int:pk>/", SalonScheduleDetailApiView.as_view()),
    path("services/", ServiceListApiView.as_view()),
    path("service/<int:pk>/", ServiceDetailApiView.as_view()),
    path("users/", UserListApiView.as_view()),

]