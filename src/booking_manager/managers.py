from django.db import models
from booking_manager.constants import ServiceStatus

class ServiceQuerySet(models.QuerySet):

    def active(self):
        return self.filter(status=ServiceStatus.ACTIVE)

    def inactive(self):
        return self.filter(status=ServiceStatus.INACTIVE)

    def archived(self):
        return self.filter(status=ServiceStatus.ARCHIVED)

    def by_category(self, category):
        return self.filter(category=category)

    def search(self, query):
        return self.filter(name__icontains=query)

    def service_optimization(self):
        return self.select_related("category").prefetch_related(
            "employee_services",
            "employee_services__employee",
        )

class ServiceManager(models.Manager):

    def get_queryset(self):
        return ServiceQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def by_category(self, category):
        return self.get_queryset().by_category(category)

    def search(self, query):
        return self.get_queryset().search(query)

    def inactive(self):
        return self.get_queryset().inactive()

    def archived(self):
        return self.get_queryset().archived()

    def service_optimization(self):
        return self.get_queryset().service_optimization()
