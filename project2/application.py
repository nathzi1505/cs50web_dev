import os

from flask import Flask, request, render_template, redirect, url_for
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

users = []
in_channels = []
messages = []

@app.route("/", methods=["GET","POST"])
def index():
    flag = 0
    if request.method == "GET":
        if len(users) == 0:
            return redirect("/register")
        return render_template("login.html")
    else:
        display = request.form.get("display")
        for user in users:
            if user == display:
                flag = 1
                return render_template("success.html", user=user)
        if flag == 0:
            return render_template("error.html", error="Display name not found", value=400)

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        display = request.form.get("display")
        if not len(users) == 0:
            for user in users:
                if (display == user):
                    return render_template("error.html", error="You have already reigstered", value=400)
        users.append(display)
        return redirect("/")

@app.route("/channels")
def channels():
    if len(in_channels) == 0:
        return render_template("channels_create.html")
    else:
        return render_template("channels.html", channels=in_channels)

@app.route("/channel_view/<int:channel_no>")
def channel_view(channel_no):
    channel_name = in_channels[channel_no]
    channel_messages = []
    for message in messages:
        string = message["message"]
        user_n = message["user"]
        time = message["time"]
        if message["no"] == channel_no:
            channel_messages.append({"message":string, "user":user_n, "time":time})
    length = len(channel_messages)
    if length > 100:
        start = length - 100
    else:
        start = 0
    return render_template("channel_view.html", channel_name=channel_name, channel_messages=channel_messages, channel_no=channel_no, start=start)

@socketio.on("submit message")
def message(data):
    message = data["message"]
    no = data["no"]
    user = data["user"]
    time = data["time"]
    messages.append({"no":int(no), "message":message, "user":user, "time":time})
    emit("announce message", {"message":message ,"user":user, "time":time}, broadcast=True)


@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        name = request.form.get("channel_name")
        for channel in in_channels:
            if name == channel:
                return render_template("error.html", error="Channel name already present", value=400)
        in_channels.append(name)
        return render_template("channels.html", channels=in_channels)
    else:
        return render_template("channels_create.html")

@socketio.on("delete")
def delete(data):
    delete_message = {}
    for message in messages:
        user_n = message["user"]
        if message["no"] == int(data["channel_no"]):
            if user_n == data["user"]:
                if message["message"]:
                    delete_message = message
    print(delete_message)
    messages.remove(delete_message)
    print(messages)
    emit("refresh", broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", debug=True, port="8080")
