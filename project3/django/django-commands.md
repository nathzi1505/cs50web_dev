Django

** All ORM commands are pointed by [O] **

// Django shell commands

django-admin startproject project-name --> Creates a django project
python3 manage.py startapp app-name --> Creates a app in that django project
python3 manage.py runserver --> Starts the web server
python3 manage.py makemigrations --> Makes the migrations in django
python3 manage.py sqlmigrate app-name migration-number(say 001) --> Helps to see the underlying sql code
python3 manage.py migrate --> Implements the migrations
python3 manage.py shell --> Starts the shell much like python3 shell
python3 manage.py createsuperuser --> Creates a superuser which has access to everything in the database

// Django database commands
f = Flight("origin" = "New York", "destination" = "New Delhi") --> Creates a Flight object
f.save() --> Much like db.commit() in flask
Flight.objects.all() --> [O] gets all the data

OR

f =/ Flight.objects.create(...) --> Creates an object of table Flight

g = Flight.objects.first() --> [O] Gets the first object in the table Flight
g.origin , g.destination --> [O] Commands to get the member values
g.delete() --> [O] Deletes that object

origin = models.ForeignKey(Airport, on_delete = CASCADE, related_name = "destination") --> on_delete helps in getting the origin synced up with Airport as if one value of Airport is deleted than the corresponding value in Flights table will also be deleted
--> related_name helps in getting the Flight object from the ForeignKey itself

k = Flight.objects.get(pk = flight_id) --> Gets an object of table Flight having primary key = flight_id

Flight.DoesNotExist --> Error flag raiser when Flight object does not exist


// Django commands
Http404("filler text") --> 404 raiser
{% url 'index' parameters %} --> points to url named index in urls.py file (APP)

{% for ... %}
{% empty %} --> Helps to print something if the for loop never ran
  ....
{% endfor %}

HttpResponseRedirect(reverse("name", args(flight_id))) --> Helps to move reverse i.e. from the name to the url

{% csrf_token %} --> To help django carry out its security against csrf attacks when submitting forms

// Bash Commands

echo $? --> Gets the return value given out by the last program
