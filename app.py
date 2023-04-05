import psycopg2
from config import DATABASE_URL
from flask import Flask, render_template, redirect, request
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
url = DATABASE_URL



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
        if not request.form.get("username"):
            return redirect("/register")
        username = request.form.get("username")
        if not request.form.get("email"):
            return redirect("/register")
        email = request.form.get("email")
        if not request.form.get("password"):
            return redirect("/register")
        password = request.form.get("password")
        print(f"{name} {surname} {username} {email} {password}")
        connection = psycopg2.connect(url)
        cursor = connection.cursor()

        # Korzystanie z bazy

        cursor.close()
        connection.close()

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

        connection = psycopg2.connect(url)
        cursor = connection.cursor()
        cursor.execute("SELECT \"User\".id_user, \"User\".password FROM \"User\" WHERE \"User\".mail = %s", [email])

        # gdy cos bedzie dodane do bazy, to dodam tu wyciagniecie hasha
        hash_from_db = 0 
        if len(cursor.fetchall()) == 1 and check_password_hash(hash_from_db):
            # Tu tez bedzie przypisanie sesji do konkretnego id usera
            # tu bedzie wyciagniecie informacji o filmach z bazy
            return render_template("main_page.html", films=[], logged_user=[])
        cursor.close()
        connection.close()
        print(f"{email} {password}")
        return redirect("/")
    else:
        return redirect("/")


if __name__ == "__main__":
    app.run()
