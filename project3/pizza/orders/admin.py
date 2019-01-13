from django.contrib import admin

from .models import Pizza, Sub, Pasta, Topping, Salad, DinnerPlatter

# Register your models here.

admin.site.register(Pizza)
admin.site.register(Sub)
admin.site.register(Topping)
admin.site.register(Pasta)
admin.site.register(Salad)
admin.site.register(DinnerPlatter)
