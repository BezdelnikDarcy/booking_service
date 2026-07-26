from django.shortcuts import render
from django.http import HttpResponse
# from booking_manager.models import Services

# Create your views here.

# def services(request):
#     context = {
#         "services": Services.objects.all(),
#
#     }
#
#
#     return render(request, 'booking_manager/services.html')
#

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def index_2(request, booking_id):
    context = {
        "booking_id" : booking_id,
    }
    return render(request, "base.html", context=context)