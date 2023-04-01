from flask import Flask, render_template, redirect

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def default():
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    return render_template("register.html")


@app.route("/main_page", methods=["GET", "POST"])
def main_page():
    return render_template("main_page.html", films=[], logged_user=[])


if __name__ == "__main__":
    app.run()
