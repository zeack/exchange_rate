from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    usage_end_date = models.DateField(null=True)
    usage = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Users"
        db_table = "user"
        ordering = ['-date_joined']

    def __str__(self):
        return self.email

    def percentage_usage(self):
        return self.usage


class ExchangeRateHistory(models.Model):
    banxico_rate = models.DecimalField(max_digits=16, decimal_places=6, default=0)
    banxico_date = models.DateField()
    banxico_last_updated = models.DateTimeField()

    dof_rate = models.DecimalField(max_digits=16, decimal_places=6, default=0)
    dof_date = models.DateField()
    dof_last_updated = models.DateTimeField()

    fixer_rate = models.DecimalField(max_digits=16, decimal_places=6, default=0)
    fixer_date = models.DateField()
    fixer_last_updated = models.DateTimeField()

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Exchange rate history"
        db_table = "exchange_rate_history"
        ordering = ['-created']

    def __str__(self):
        return str(self.created)


class ApiKey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='keys')
    name = models.CharField(max_length=100)
    api_key = models.UUIDField(null=True)

    class Meta:
        verbose_name_plural = "Api keys"
        db_table = "api_key"
        ordering = ['name']

    def __str__(self):
        return str(self.name)
