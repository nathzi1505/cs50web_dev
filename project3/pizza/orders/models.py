from django.db import models

# Create your models here.
class Pizza(models.Model):
    name = models.CharField(max_length=64)
    type = models.CharField(max_length=64)
    toppings = models.IntegerField()
    small = models.FloatField()
    large = models.FloatField()

    def __str__(self):
        return (f"{self.name} {self.type} {self.toppings}")

class Topping(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return (f"{self.name}")

class Sub(models.Model):
    name = models.CharField(max_length=64)
    small = models.FloatField()
    large = models.FloatField()
    extra_cheese = models.BooleanField(default=False)

    def __str__(self):
        return (f"{self.name} {self.extra_cheese}")

class Pasta(models.Model):
    name = models.CharField(max_length=64)
    price = models.FloatField()

    def __str__(self):
        return (f"{self.name}")

class Salad(models.Model):
    name = models.CharField(max_length=64)
    price = models.FloatField()

    def __str__(self):
        return (f"{self.name}")

class DinnerPlatter(models.Model):
    name = models.CharField(max_length=64)
    small = models.FloatField()
    large = models.FloatField()

    def __str__(self):
        return (f"{self.name}")
