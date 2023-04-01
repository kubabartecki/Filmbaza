from flask import Flask, render_template, redirect

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def login():
    return render_template("login.html")


if __name__ == "__main__":
    app.run()
