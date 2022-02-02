from datetime import datetime, timedelta

from django.db import models
from django.utils.timezone import utc
from django.contrib.auth.models import AbstractUser
from django.conf import settings


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

    def reset_usage(self):
        """ Reset the user's usage. """
        today = datetime.utcnow().replace(tzinfo=utc).date()
        self.usage_end_date = today + timedelta(days=30)
        self.usage = 0
        self.save(update_fields=['usage_end_date', 'usage'])

    def check_usage_limit(self):
        """ Check if the user has reached his usage limit. 
        If the user has reached his usage limit, return True. """
        today = datetime.utcnow().replace(tzinfo=utc).date()
        if self.usage_end_date is None or self.usage is None:
            self.reset_usage()
            return False

        elif today >= self.usage_end_date:
            self.reset_usage()
            return False
        
        elif (
            self.usage_end_date  > today 
            and settings.MAX_REQUEST_USAGE > self.usage
        ):
            return False
        
        else:
            return True


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
