from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from .models import *

shopping_cart = []
shopping_cart_user = []
temp_cart = []
duplicates = []
order = []
user = 0
order_no = 0
pizza_a = [0] * 10000000
salad = [0] * 10000000
dinner = [0] * 10000000
sub = [0] * 10000000
pasta = [0] * 10000000
active = [0] * 10000000
total = [0] * 10000000

# Handles the index page
def index(request):
    if user == 0:
        return HttpResponseRedirect("login")

    if request.method == "GET":
        if not request.user.is_authenticated:
            return HttpResponseRedirect("login")
        else:
            context = {
                "pizzas":Pizza.objects.all(),
                "subs":Sub.objects.all().filter(extra_cheese = False),
                "subs_e":Sub.objects.all().filter(extra_cheese = True),
                "pastas":Pasta.objects.all(),
                "salads":Salad.objects.all(),
                "dinners":DinnerPlatter.objects.all()
            }
            return render(request, "orders/index.html", context)

# Handles the shopping cart for items other than pizza
def shopping(request, item_no, large = 0):
    if user == 0:
        return HttpResponseRedirect("login")

    global duplicates
    global total
    global shopping_cart
    global shopping_cart_user
    duplicates.clear()
    shopping_cart.clear()
    shopping_cart_user.clear()

    global active
    active[user.id] = 1
    total[user.id] = 0

    flag = 0
    total_p = 0
    val = item_no // 100

    global temp_cart

    if val == 4 or val == 5 or val == 40 or val == 50:
        global sub
        sub[user.id] = 1
        id = item_no - (val*100)
        if val == 4:
            item = Sub.objects.get(pk=id)
            temp_cart.append({"user":user, "item_class":"sub", "name":item.name, "qty": 0, "size":"Small", "price":item.small, "extra_cheese":"No", "toppings":None})
        elif val == 5:
            item = Sub.objects.get(pk=id)
            temp_cart.append({"user":user, "item_class":"sub", "name":item.name, "qty": 0, "size":"Large", "price":item.large, "extra_cheese":"No", "toppings":None})
        elif val == 40:
            item = Sub.objects.get(pk=(id + 18))
            temp_cart.append({"user":user, "item_class":"sub", "name":item.name, "qty": 0, "size":"Small", "price":item.small, "extra_cheese":"Yes", "toppings":None})
        elif val == 50:
            item = Sub.objects.get(pk=(id + 18))
            temp_cart.append({"user":user, "item_class":"sub", "name":item.name, "qty": 0, "size":"Large", "price":item.large, "extra_cheese":"Yes", "toppings":None})

    if val == 6:
        global pasta
        pasta[user.id] = 1
        id=item_no - (val*100)
        item = Pasta.objects.get(pk=id)
        temp_cart.append({"user":user, "item_class":"pasta", "size":None, "name":item.name, "qty": 0, "price":item.price, "extra_cheese":None, "toppings":None})

    if val == 7 or val == 9:
        global dinner
        dinner[user.id] = 1
        id = item_no - (val*100)
        item = DinnerPlatter.objects.get(pk=id)
        if val == 7:
            temp_cart.append({"user":user, "item_class":"dinner_platter", "name":item.name, "qty": 0, "size":"Small", "price":item.small, "extra_cheese":None, "toppings":None})
        else:
            temp_cart.append({"user":user, "item_class":"dinner_platter", "name":item.name, "qty": 0, "size":"Large", "price":item.large, "extra_cheese":None, "toppings":None})

    if val == 8:
        global salad
        salad[user.id] = 1
        id=item_no - (val*100)
        item = Salad.objects.get(pk=id)
        temp_cart.append({"user":user, "item_class":"salad", "size":None, "name":item.name, "qty":0, "price":item.price, "extra_cheese":None, "toppings":None})

    for item1 in temp_cart:
        for dup in duplicates:
            if item1 == dup:
                flag = 1
        if flag == 0:
            qty = item1["qty"]
            for item2 in temp_cart:
                if item1 == item2:
                        qty = qty + 1
            shopping_cart.append({"user":item1["user"], "item_class":item1["item_class"], "name":item1["name"], "size":item1["size"], "price":item1["price"], "qty":qty, "total":(item1["price"] * qty), "extra_cheese":item1["extra_cheese"],  "toppings":item1["toppings"]})
            total[item1["user"].id] = total[item1["user"].id] + (item1["price"] * qty)
            duplicates.append(item1)
        flag = 0

    for item in shopping_cart:
        if item["user"] == user:
            shopping_cart_user.append(item)

    context = {
        "shopping_cart":shopping_cart_user,
        "pizza_active":pizza_a[user.id],
        "salad_active":salad[user.id],
        "sub_active":sub[user.id],
        "dinner_active":dinner[user.id],
        "pasta_active":pasta[user.id],
        "active":active[user.id],
        "total":total[user.id]
    }
    return render(request, "orders/shopping.html", context)

# Handles the pizza orders
def toppings(request, item_no):
    if user == 0:
        return HttpResponseRedirect("login")

    global duplicates
    global shopping_cart
    global shopping_cart_user
    duplicates.clear()
    shopping_cart.clear()
    shopping_cart_user.clear()

    global active
    active[user.id] = 1

    global total
    total[user.id] = 0

    toppings = []
    global temp_cart
    global pizza_a
    val = item_no // 1000
    id = item_no - (val*1000)
    pizza = Pizza.objects.get(pk = id)

    if request.method == "GET":
        word = ""
        for i in range(0,pizza.toppings):
            word = word + "x"

        if not pizza.toppings == 0:
            return render(request, "orders/toppings.html", {"item_no":item_no, "no":pizza.toppings, "word":word, "toppings":Topping.objects.all()})

    size = "Small"
    toppings = []
    price = pizza.small
    flag = 0

    if (val == 2):
        size = "Large"
        price = pizza.large

    if not pizza.toppings == 0:
        for i in range(0,pizza.toppings):
            v = str(i + 1)
            toppings.append(request.POST[v])
        pizza_a[user.id] = 1
        temp_cart.append({"user":user, "item_class":"pizza", "name":pizza.name, "size":size, "price":price, "qty":0, "extra_cheese":None, "toppings": toppings})
    else:
        pizza_a[user.id] = 1
        temp_cart.append({"user":user, "item_class":"pizza", "name":pizza.name, "size":size, "price":price, "qty":0, "extra_cheese":None, "toppings": None})

    for item1 in temp_cart:
        for dup in duplicates:
            if item1 == dup:
                flag = 1
        if flag == 0:
            qty = item1["qty"]
            for item2 in temp_cart:
                if item1 == item2:
                        qty = qty + 1
            shopping_cart.append({"user":item1["user"], "item_class":item1["item_class"], "name":item1["name"], "size":item1["size"], "price":item1["price"], "qty":qty, "total":(item1["price"]*qty), "extra_cheese":None, "toppings": item1["toppings"]})
            total[item1["user"].id] = total[item1["user"].id] + (item1["price"] * qty)
            duplicates.append(item1)
        flag = 0

    shopping_cart_user = []
    for item in shopping_cart:
        if item["user"] == user:
            shopping_cart_user.append(item)

    context = {
        "shopping_cart":shopping_cart_user,
        "pizza_active":pizza_a[user.id],
        "salad_active":salad[user.id],
        "sub_active":sub[user.id],
        "dinner_active":dinner[user.id],
        "pasta_active":pasta[user.id],
        "active":active[user.id],
        "total":total[user.id]
    }
    return render(request, "orders/shopping.html", context)

# Shows the shopping cart
def shopping_view(request):
    if user == 0:
        return HttpResponseRedirect("login")
    context = {
        "shopping_cart":shopping_cart_user,
        "pizza_active":pizza_a[user.id],
        "salad_active":salad[user.id],
        "sub_active":sub[user.id],
        "dinner_active":dinner[user.id],
        "pasta_active":pasta[user.id],
        "active":active[user.id],
        "total":total[user.id]
    }
    return render(request, "orders/shopping.html", context)

# Shows the confirmation page
def confirm(request):
    if user == 0:
        return HttpResponseRedirect("login")
    global shopping_cart_user
    global pizza_a
    global salad
    global sub
    global dinner
    global pasta
    global active
    global total
    if request.method == "GET":
        context = {
            "shopping_cart":shopping_cart_user,
            "pizza_active":pizza_a[user.id],
            "salad_active":salad[user.id],
            "sub_active":sub[user.id],
            "dinner_active":dinner[user.id],
            "pasta_active":pasta[user.id],
            "active":active[user.id],
            "total":total[user.id]
        }
        return render(request, "orders/confirm.html", context)
    else:
        global order_no
        order_no = order_no + 1
        global order
        contents = []
        for item in shopping_cart_user:
            contents.append(item)
        order.append({"no":order_no, "total":total, "user": user, "contents":contents})

        body = "Your order no: " + str(order_no) + " has been placed! Thanks for ordering with us!"
        email = EmailMessage("Pinnochio's Pizza Order", body, to=[user.email])
        email.send()

        shopping_cart_user.clear()
        total[user.id] = 0
        active[user.id] = 0
        pasta[user.id] = 0
        dinner[user.id] = 0
        sub[user.id] = 0
        salad[user.id] = 0
        pizza_a[user.id] = 0

        logout(request)
        return render(request, "orders/thankyou.html")

# Handles the order placement for site administrators
def placed(request):
    if user == 0:
        return HttpResponseRedirect("login")
    if user.is_staff:
        global order
        if request.method == "GET":
            context = {
                "orders":order
            }
            return render(request, "orders/placed.html", context)
        else:
            global temp_cart
            items = []
            val = request.POST["order_no"]
            for item in order:
                if not item["no"] == int(val):
                    items.append(item)

            order.clear()
            order = items
            context = {
                "orders":order
            }

            items = []
            for item in temp_cart:
                if not item["user"] == user:
                    items.append(item)

            temp_cart = items
            return render(request, "orders/placed.html", context)
    else:
        return render(request, "orders/forbidden.html")

# Handles the registration page
def register(request):
    if request.method == "GET":
        return render(request, "orders/register.html")

    username = request.POST["username"]
    password = request.POST["password"]
    first = request.POST["first"]
    last = request.POST["last"]
    email = request.POST["email"]
    global user
    user = User.objects.create_user(username=username, email=email, password=password)
    user.first_name = first
    user.last_name = last
    user.save()
    login(request, user)
    return HttpResponseRedirect("/")

# Handles the login page
def login_view(request):
    if request.method == "GET":
        return render(request, "orders/login.html")
    username = request.POST["username"]
    password = request.POST["password"]
    global user
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        if user.is_staff:
            return HttpResponseRedirect("/placed")
        else:
            return HttpResponseRedirect("/")
    else:
        return render(request, "orders/login.html", {"message" : "Invalid credentials", "error" : 1})

# Handles the logout page
def logout_view(request):
    logout(request)
    return render(request, "orders/logout.html")
