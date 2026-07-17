from django.db import models

from config.models import BaseModel


class Categories(BaseModel):
    name = models.CharField(
        max_length=64,
        unique=True,
        verbose_name="Наименование"
    )
    description = models.TextField(
        null=True,
        verbose_name="Описание"
    )

    is_active = models.BooleanField(default=True)



    class Meta:
        ordering = ('name',)
        db_table = 'categories'
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name