from flask import Flask, render_template, redirect, request

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def default():
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if not request.form.get("name"):
            return redirect("/register")
        name = request.form.get("name")
        if not request.form.get("surname"):
            return redirect("/register")
        surname = request.form.get("surname")
        if not request.form.get("email"):
            return redirect("/register")
        email = request.form.get("email")
        if not request.form.get("password"):
            return redirect("/register")
        password = request.form.get("password")
        print(f"{name} {surname} {email} {password}")
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/main_page", methods=["GET", "POST"])
def main_page():
    if request.method == "POST":
        if not request.form.get("email"):
            return redirect("/")
        email = request.form.get("email")
        if not request.form.get("password"):
            return redirect("/")
        password = request.form.get("password")
        print(f"{email} {password}")
        return render_template("main_page.html", films=[], logged_user=[])
    else:
        return redirect("/")


if __name__ == "__main__":
    app.run()
