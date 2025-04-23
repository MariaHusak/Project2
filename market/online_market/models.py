from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_set",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions_set",
        blank=True
    )

    bike_orders = models.ManyToManyField("BikeOrder", related_name="users", blank=True) 

    def __str__(self):
        return self.username


class BikeOrder(models.Model):
    BIKE_TYPE_CHOICES = [
        ('regular', 'Regular Bike'),
        ('electric', 'Electric Bike'),
    ]
    bike_type = models.CharField(max_length=8, choices=BIKE_TYPE_CHOICES)
    frame = models.CharField(max_length=20)
    wheels = models.CharField(max_length=20)
    motor = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.bike_type} - {self.frame} frame, {self.wheels} wheels" + (f", {self.motor}" if self.motor else "")