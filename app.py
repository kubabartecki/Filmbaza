from flask import Flask, render_template, redirect, request

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def default():
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        surname = request.form.get("surname")
        email = request.form.get("email")
        password = request.form.get("password")
        print(f"{name} {surname} {email} {password}")
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/main_page", methods=["GET", "POST"])
def main_page():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        print(f"{email} {password}")
        return render_template("main_page.html", films=[], logged_user=[])
    else:
        return redirect("/")


if __name__ == "__main__":
    app.run()
