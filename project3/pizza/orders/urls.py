from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("register", views.register, name="register"),
    path("logout", views.logout_view, name="logout"),
    path("<int:item_no>", views.shopping, name="shopping"),
    path("<int:item_no>_toppings", views.toppings, name="toppings"),
    path("shopping", views.shopping_view, name="shopping_view"),
    path("confirm", views.confirm, name="confirm"),
    path("placed", views.placed, name="placed")
]
