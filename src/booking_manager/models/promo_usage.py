from django.db import models
from config.models import BaseModel



class PromoUsage(BaseModel):
    promo = models.ForeignKey(
        to = "PromoCodes",
        on_delete=models.PROTECT,
        related_name="promo_usages",
        verbose_name="Промокод"
    )

    client = models.ForeignKey(
        to = "account.ClientProfile",
        on_delete=models.PROTECT,
        related_name="promo_usages",
        verbose_name="Клиент"
    )

    booking = models.ForeignKey(
        to = "Bookings",
        on_delete=models.PROTECT,
        related_name = "promo_usages",
        verbose_name="Запись"
    )

    class Meta:
        ordering = ["-created_at"]
        db_table = "promo_usage"
        verbose_name = "История использования промокодов"
        verbose_name_plural = "Истории использования промокодов"
        constraints = [
            models.UniqueConstraint(
                fields=["promo", "client"],
                name="unique_client_promo_usage"
            )
        ]